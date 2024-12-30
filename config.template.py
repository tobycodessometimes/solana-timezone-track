# config.template.py
# Copy this file to config.py and update with your settings

# Your RPC endpoint URL (get one from helius.dev or another provider)
RPC_URL = "YOUR_RPC_URL_HERE"

# List of wallet addresses to track (one per line for readability)
WALLET_ADDRESSES = [
    "YOUR_WALLET_ADDRESS_1_HERE",
    "YOUR_WALLET_ADDRESS_2_HERE"  # Add more addresses as needed
]

# These default settings (adjust however you want)
REQUEST_DELAY = 0.5          # Delay between requests (in seconds)
RETRY_DELAY = 3.0             # Delay when rate limited (in seconds)
MAX_RETRIES = 5               # Number of retries per request
MAX_CONCURRENT_REQUESTS = 15    # Maximum parallel requests
BATCH_SIZE = 7               # Number of transactions to process at once
SIGNATURE_BATCH_SIZE = 25     # Number of signatures to fetch per request
# These settings work for helius free tier at 3tx/s. Nothing special though so you can play around.

"""
Tuning Guide
-----------
If you're getting rate limited:
- Increase REQUEST_DELAY (e.g., from 1.0 to 2.0)
- Decrease MAX_CONCURRENT_REQUESTS (e.g., from 5 to 3)

If you have a paid RPC and want faster processing:
- Decrease REQUEST_DELAY 
- Increase MAX_CONCURRENT_REQUESTS
- Increase BATCH_SIZE
Adjust and figure it out yourself.
"""   
