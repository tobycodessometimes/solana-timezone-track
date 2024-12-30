import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from config import WALLET_ADDRESSES

# Load data from filtered_transactions.json
input_file = "filtered_transactions.json"

def load_transaction_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def plot_hourly_activity(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    df['time_sent'] = pd.to_datetime(df['time_sent'])
    df['hour'] = df['time_sent'].dt.hour

    # Create figure with larger size
    plt.figure(figsize=(15, 8))

    # Get unique hours from 0 to 23
    all_hours = np.arange(24)
    
    # Calculate total transactions per hour first
    total_transactions = np.zeros(24)
    for wallet in WALLET_ADDRESSES:
        wallet_data = df[df['sending_address'] == wallet]
        hourly_counts = wallet_data.groupby('hour').size()
        hourly_counts = hourly_counts.reindex(all_hours, fill_value=0)
        total_transactions += hourly_counts

    # Add gray background for inactive hours
    max_height = max(total_transactions) if len(total_transactions) > 0 else 1
    inactive_hours = [hour for hour in all_hours if total_transactions[hour] == 0]
    for i in range(len(inactive_hours)):
        if i == 0 or inactive_hours[i] > inactive_hours[i-1] + 1:
            start = inactive_hours[i]
            end = start + 1
            while i < len(inactive_hours) - 1 and inactive_hours[i+1] == inactive_hours[i] + 1:
                end += 1
                i += 1
            plt.axvspan(start - 0.4, end - 0.6, color='lightgray', alpha=0.3, label='Inactive Hours' if start == inactive_hours[0] else "")

    # Plot stacked bars for each wallet
    bar_width = 0.8
    bottom = np.zeros(24)
    colors = ['crimson' if len(WALLET_ADDRESSES) == 1 else plt.cm.Set3(i) for i in np.linspace(0, 1, len(WALLET_ADDRESSES))]
    
    for wallet_idx, wallet in enumerate(WALLET_ADDRESSES):
        wallet_data = df[df['sending_address'] == wallet]
        hourly_counts = wallet_data.groupby('hour').size()
        hourly_counts = hourly_counts.reindex(all_hours, fill_value=0)
        
        # Add transaction count on top of bars
        for hour in all_hours:
            if hourly_counts[hour] > 0:
                plt.text(hour, bottom[hour] + hourly_counts[hour]/2, 
                        int(hourly_counts[hour]), ha='center', va='center', color='white')
        
        plt.bar(all_hours, hourly_counts, bottom=bottom, 
                width=bar_width, color=colors[wallet_idx],
                label=f'Wallet {wallet[:4]}...{wallet[-4:]}' if len(WALLET_ADDRESSES) > 1 else None)
        bottom += hourly_counts

    # Calculate average for the line
    avg_transactions = total_transactions[total_transactions > 0].mean()

    # Add average line
    plt.axhline(y=avg_transactions, color='blue', linestyle='--', alpha=0.7,
                label=f'Average ({avg_transactions:.1f})')

    # Customize the plot
    if len(WALLET_ADDRESSES) == 1:
        plt.title(f'Hourly Transaction Activity\nWallet: {WALLET_ADDRESSES[0][:8]}...', 
                 fontsize=14, pad=20)
    else:
        plt.title('Hourly Transaction Activity', fontsize=14, pad=20)
    
    plt.xlabel('Hour of Day (24-hour format)', fontsize=12)
    plt.ylabel('Number of Transactions', fontsize=12)
    
    # Set x-axis ticks
    plt.xticks(all_hours)
    
    # Add legend if needed
    if len(WALLET_ADDRESSES) > 1:
        plt.legend(bbox_to_anchor=(1.05, 0.7), loc='upper left')
    else:
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles, labels, bbox_to_anchor=(1.05, 0.7), loc='upper left')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show grid
    plt.grid(True, alpha=0.3)
    
    # Save and show the plot
    plt.savefig('transaction_activity.png', bbox_inches='tight', dpi=300)
    plt.show()

if __name__ == "__main__":
    # Load data and generate the chart
    transactions = load_transaction_data(input_file)
    plot_hourly_activity(transactions)
