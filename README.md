# Solana Transaction Timezone Tracker

A tool that logs all outgoing transactions for a list of Solana wallet/s. This allows you to track the activity and chart the time of day of transactions. Hopefully, this will be a simple way to identify the timezone of a wallet, and potentially develop a further answer to confirm the timezone of a wallet. 

Features include:
- Multi-wallet support
- Parallel transaction processing
- Hourly activity visualization
- Transaction amount tracking
- Configurable RPC settings

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/solana-transaction-tracker
   cd solana-transaction-tracker
   ```

2. **Set Up Python Environment**
   - Requires Python 3.7+
   - Install required packages:
     ```bash
     pip install requests pandas matplotlib tqdm aiohttp
     ```

3. **Configure Settings**
   - Copy `config.template.py` to `config.py`:
     ```bash
     cp config.template.py config.py
     ```
   - Edit `config.py` with your settings:
     - Add your RPC URL (get one from [helius.dev](https://helius.dev) or another provider)
     - Add your wallet addresses
     - Adjust RPC settings if needed

## Usage

1. **Fetch Transactions**
   ```bash
   python index.py
   ```
   This will:
   - Download transactions for all configured wallets
   - Filter for outgoing transfers
   - Save results to `filtered_transactions.json`

2. **View Transaction Charts**
   ```bash
   python chart_transactions.py
   ```
   Creates a visualization showing:
   - Transaction activity by hour
   - Different colors for each wallet
   - Inactive periods in gray
   - Average transaction line
   - Transaction counts on bars

## Configuration Options

In `config.py`:
```python
RPC_URL = "YOUR_RPC_URL"  # Your RPC endpoint
WALLET_ADDRESSES = [       # List of wallets to track
    "address1",
    "address2"
]
REQUEST_DELAY = 0.05      # Delay between requests
RETRY_DELAY = 1          # Retry delay when rate limited
MAX_RETRIES = 5         # Max retries per request
```

### RPC Settings Guide
- **Public RPCs**: Use higher delays (0.5-1.0 seconds)
- **Private RPCs**: Can use lower delays (0.05-0.1 seconds)
- Adjust based on your RPC provider's rate limits

## Output Files

1. **filtered_transactions.json**
   - Contains all outgoing transfers
   - Fields:
     - `receiver_address`: Recipient wallet
     - `sending_address`: Sender wallet
     - `sending_amount`: Amount in SOL
     - `time_sent`: Transaction timestamp

2. **transaction_activity.png**
   - Visual chart of transaction activity
   - Shows hourly distribution
   - Multi-wallet color coding
   - Average transaction line

## Troubleshooting

1. **Rate Limits**
   - Increase `REQUEST_DELAY` in config.py
   - Use a private RPC endpoint
   - Reduce number of concurrent requests

2. **Performance**
   - Adjust `batch_size` in index.py
   - Modify `MAX_RETRIES` for stability
   - Use SSD for faster file operations

## Contributing

Contributions are welcome! I know the code is not perfect, but it works.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 