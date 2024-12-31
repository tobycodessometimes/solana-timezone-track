# Solana Transaction Timezone Tracker

A tool that logs outgoing transactions from Solana wallets and visualizes their activity patterns by hour. Useful for analyzing wallet activity patterns and potentially identifying user timezones.

Single wallet example:
![8zZ](https://github.com/user-attachments/assets/6873051b-d1fa-4197-8103-1101fd929885)

Comparing relationships between wallets example:
![C3R](https://github.com/user-attachments/assets/bcb09b13-eab7-42ca-b31f-265ad77684d2)

Mutli wallet support example:
<img width="1122" alt="multi" src="https://github.com/user-attachments/assets/9072f8be-7989-4759-8d04-23413b4ef2a1" />

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
