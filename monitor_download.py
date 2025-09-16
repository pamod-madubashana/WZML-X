#!/usr/bin/env python3
"""
Monitor the download progress of the Telegram file
"""

import time
from bot_api_client import BotAPIClient

def monitor_download():
    """Monitor the download progress"""
    print("Monitoring Telegram File Download Progress")
    print("=" * 50)
    
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    
    # Initialize the client
    client = BotAPIClient(BASE_URL, API_SECRET)
    
    # Check initial status
    status = client.get_status()
    if status.get('status') == 'success':
        print(f"Bot Status: {status['bot_status']}")
        print(f"Active Downloads: {status['active_downloads']}")
    else:
        print(f"Error checking status: {status.get('error', 'Unknown error')}")
        return
    
    print("\nMonitoring download progress (Ctrl+C to stop)...")
    print("-" * 50)
    
    try:
        while True:
            # Get current downloads
            downloads = client.get_downloads()
            if downloads.get('status') == 'success':
                count = downloads.get('count', 0)
                if count > 0:
                    download_list = downloads.get('downloads', [])
                    for i, download in enumerate(download_list, 1):
                        name = download.get('name', 'Unknown')
                        progress = download.get('progress', '0%')
                        speed = download.get('speed', '0 B/s')
                        eta = download.get('eta', 'Unknown')
                        status = download.get('status', 'Unknown')
                        
                        print(f"[{i}] {name}")
                        print(f"    Progress: {progress} | Speed: {speed} | ETA: {eta} | Status: {status}")
                        print()
                else:
                    print("No active downloads")
            else:
                print(f"Error getting downloads: {downloads.get('error', 'Unknown error')}")
            
            # Wait before next check
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError during monitoring: {e}")

if __name__ == "__main__":
    monitor_download()