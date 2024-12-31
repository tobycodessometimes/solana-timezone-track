import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone
from config import (
    RPC_URL, WALLET_ADDRESSES, REQUEST_DELAY, RETRY_DELAY, MAX_RETRIES,
    MAX_CONCURRENT_REQUESTS, BATCH_SIZE, SIGNATURE_BATCH_SIZE
)
from tqdm import tqdm

output_file = "filtered_transactions.json"
headers = {"Content-Type": "application/json"}

async def fetch_with_retry(session, url, payload, max_retries=MAX_RETRIES):
    last_error = None
    for attempt in range(max_retries):
        try:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 429:  # Rate limit
                    tqdm.write(f"Rate limited, waiting {RETRY_DELAY}s...")
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                if response.status != 200:
                    tqdm.write(f"Error {response.status}, retrying...")
                    await asyncio.sleep(REQUEST_DELAY)
                    continue
                return await response.json()
        except asyncio.TimeoutError:
            last_error = "Timeout"
            await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                await asyncio.sleep(REQUEST_DELAY)
            else:
                tqdm.write(f"Error after {max_retries} retries: {last_error}")
    return None

async def fetch_signatures(session, address, rpc_url, semaphore):
    all_signatures = []
    before = None
    retries = 0
    max_fetch_retries = 3
    seen_signatures = set()
    
    with tqdm(desc=f"Fetching {address[:4]}...", unit="sig", leave=False) as pbar:
        while True:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [address, {"limit": SIGNATURE_BATCH_SIZE, "before": before}]
            }
            
            async with semaphore:
                result = await fetch_with_retry(session, rpc_url, payload)
                
                if not result:
                    if retries < max_fetch_retries:
                        retries += 1
                        tqdm.write(f"Retrying signature fetch for {address[:4]} (attempt {retries}/{max_fetch_retries})")
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    break
                
                signatures = result.get("result", [])
                if not signatures:
                    break
                
                # Filter out duplicates
                new_signatures = []
                for sig in signatures:
                    signature = sig["signature"]
                    if signature not in seen_signatures:
                        seen_signatures.add(signature)
                        new_signatures.append(sig)
                
                if new_signatures:
                    all_signatures.extend(new_signatures)
                    before = new_signatures[-1]["signature"]
                    pbar.update(len(new_signatures))
                else:
                    break  # No new signatures found
                    
                await asyncio.sleep(REQUEST_DELAY)
                retries = 0  # Reset retries on successful fetch

    tqdm.write(f"Found {len(all_signatures)} unique signatures for {address[:4]}...")
    return all_signatures

async def fetch_transaction_batch(session, signatures, rpc_url, semaphore, pbar):
    tasks = []
    failed_signatures = []
    seen_transactions = set()
    
    async def fetch_single(signature):
        retries = 0
        max_tx_retries = 3
        
        while retries < max_tx_retries:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
                }
                
                async with semaphore:
                    result = await fetch_with_retry(session, rpc_url, payload)
                    if result and result.get("result"):
                        tx = result.get("result")
                        tx_key = f"{tx.get('blockTime', '')}_{tx['transaction']['signatures'][0]}"
                        if tx_key not in seen_transactions:
                            seen_transactions.add(tx_key)
                            pbar.update(1)
                            return tx
                    
                    # If we get here, either no result or already seen
                    if retries < max_tx_retries - 1:
                        retries += 1
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    else:
                        failed_signatures.append(signature)
                        return None
                        
            except Exception as e:
                if retries < max_tx_retries - 1:
                    retries += 1
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                else:
                    tqdm.write(f"Error fetching transaction {signature[:8]}: {str(e)}")
                    failed_signatures.append(signature)
                    return None
    
    # Process transactions in smaller sub-batches to avoid overwhelming the RPC
    sub_batch_size = 2
    for i in range(0, len(signatures), sub_batch_size):
        sub_batch = signatures[i:i + sub_batch_size]
        sub_tasks = [fetch_single(sig["signature"]) for sig in sub_batch]
        results = await asyncio.gather(*sub_tasks)
        tasks.extend(results)
        
        # Add a small delay between sub-batches
        if i + sub_batch_size < len(signatures):
            await asyncio.sleep(REQUEST_DELAY)
    
    valid_results = [r for r in tasks if r]
    
    if failed_signatures:
        tqdm.write(f"Failed to fetch {len(failed_signatures)} transactions after retries")
    
    return valid_results

async def process_wallet(session, wallet_address, semaphore):
    print(f"\nProcessing wallet: {wallet_address}")
    
    # Fetch signatures
    signatures = await fetch_signatures(session, wallet_address, RPC_URL, semaphore)
    if not signatures:
        print(f"No signatures found for {wallet_address}")
        return []
    
    # Process transactions in optimized batches
    transactions = []
    signature_batches = [signatures[i:i + BATCH_SIZE] for i in range(0, len(signatures), BATCH_SIZE)]
    
    with tqdm(total=len(signatures), desc=f"Fetching {wallet_address[:4]}...", unit="tx", leave=False) as pbar:
        for batch in signature_batches:
            batch_results = await fetch_transaction_batch(session, batch, RPC_URL, semaphore, pbar)
            transactions.extend(batch_results)
            await asyncio.sleep(REQUEST_DELAY)
    
    return transactions

def extract_transaction_data(transaction, wallet_address):
    try:
        message = transaction["transaction"]["message"]
        meta = transaction.get("meta", {})
        if not meta:
            return []
            
        time_sent = transaction.get("blockTime", None)
        if not time_sent:
            return []
            
        time_sent = datetime.fromtimestamp(time_sent, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        account_keys = message["accountKeys"]
        instructions = message.get("instructions", [])
        
        if not instructions:
            return []

        filtered_data = []
        seen_transfers = set()
        
        for ix in instructions:
            try:
                program_id_index = ix["programIdIndex"]
                program_id = account_keys[program_id_index]

                if program_id == "11111111111111111111111111111111":  # System Program
                    accounts = ix.get("accounts", [])
                    if len(accounts) >= 2:
                        sender = account_keys[accounts[0]]
                        receiver = account_keys[accounts[1]]
                        
                        if sender == wallet_address:
                            pre_balance = meta["preBalances"][accounts[0]]
                            post_balance = meta["postBalances"][accounts[0]]
                            amount_sent = (pre_balance - post_balance) / 1e9
                            
                            if amount_sent > 0:  # Only include positive transfers
                                transfer_key = f"{time_sent}_{sender}_{receiver}_{amount_sent}"
                                if transfer_key not in seen_transfers:
                                    seen_transfers.add(transfer_key)
                                    filtered_data.append({
                                        "receiver_address": receiver,
                                        "sending_address": sender,
                                        "sending_amount": amount_sent,
                                        "time_sent": time_sent,
                                        "wallet_index": WALLET_ADDRESSES.index(wallet_address)
                                    })
            except (KeyError, IndexError) as e:
                continue  # Skip malformed instructions
                
        return filtered_data
    except Exception as e:
        tqdm.write(f"Error processing transaction: {e}")
        return []

async def main_async():
    print("\nStarting transaction fetch process...")
    
    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Configure session with connection pooling and longer timeouts
    connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=60, connect=30, sock_read=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Process all wallets concurrently
        tasks = [process_wallet(session, wallet, semaphore) for wallet in WALLET_ADDRESSES]
        all_results = await asyncio.gather(*tasks)
    
    # Combine and filter results
    filtered_transactions = []
    total_processed = 0
    seen_transactions = set()
    
    for wallet_idx, transactions in enumerate(all_results):
        wallet = WALLET_ADDRESSES[wallet_idx]
        total_processed += len(transactions)
        
        # Filter transactions
        wallet_filtered = []
        with tqdm(total=len(transactions), desc=f"Filtering {wallet[:4]}...", unit="tx", leave=False) as pbar:
            for tx in transactions:
                filtered = extract_transaction_data(tx, wallet)
                for f in filtered:
                    tx_key = f"{f['time_sent']}_{f['sending_address']}_{f['receiver_address']}_{f['sending_amount']}"
                    if tx_key not in seen_transactions:
                        seen_transactions.add(tx_key)
                        wallet_filtered.append(f)
                pbar.update(1)
        
        filtered_transactions.extend(wallet_filtered)
        print(f"Found {len(wallet_filtered)} unique filtered transactions from {len(transactions)} total for {wallet[:4]}...")
    
    # Save results
    print(f"\nProcessed {total_processed} total transactions")
    print("\nSaving filtered transactions...")
    with open(output_file, "w") as file:
        json.dump(filtered_transactions, file, indent=4)
    
    print(f"\nSuccessfully saved {len(filtered_transactions)} unique filtered transactions")

def main():
    # Increase default limits for Windows
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run
    asyncio.run(main_async())

if __name__ == "__main__":
    main()