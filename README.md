# Solana Transaction Timezone Tracker

A tool that logs outgoing transactions from Solana wallets and visualizes their activity patterns by hour. Useful for analyzing wallet activity patterns and potentially identifying user timezones.

## Features
- Multi-wallet tracking
- Activity visualization by hour
- Transaction amount tracking
- Configurable RPC settings
- Duplicate transaction handling
- Rate limit management

## Setup

1. **Install Requirements**
   ```bash
   pip install aiohttp pandas matplotlib tqdm
   ```

2. **Configure Settings**
   - Copy `config.template.py` to `config.py`
   - Add your RPC URL (get one from [helius.dev](https://helius.dev))
   - Add wallet addresses to track
   ```python
   RPC_URL = "YOUR_RPC_URL"
   WALLET_ADDRESSES = [
       "wallet1",
       "wallet2"
   ]
   ```

## Usage

1. **Fetch Transactions**
   ```bash
   python index.py
   ```
   - Downloads and filters outgoing transactions
   - Saves to `filtered_transactions.json`

2. **Generate Chart**
   ```bash
   python chart_transactions.py
   ```
   - Creates `transaction_activity.png`
   - Shows hourly transaction patterns
   - Different colors per wallet
   - Includes inactive hours and averages

## Output Files
- `filtered_transactions.json`: Transaction data
- `transaction_activity.png`: Activity visualization

## Performance Tuning

Default settings in `config.py` work with Helius free tier. Adjust if needed:

```python
# Slower but reliable (free RPCs)
REQUEST_DELAY = 1.0
MAX_CONCURRENT_REQUESTS = 5

# Faster (paid RPCs)
REQUEST_DELAY = 0.1
MAX_CONCURRENT_REQUESTS = 25
```

## License
MIT License 