#!/usr/bin/env python3
"""
Specific example to leech a Telegram file: https://t.me/c/3021633087/50
This demonstrates the real functionality of the bot API client.
"""

import time
import json
from bot_api_client import BotAPIClient

def leech_telegram_file():
    """Leech the specific Telegram file requested by the user"""
    # Configuration - Update these values as needed
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    CHAT_ID = "-1002934661749"  # Your supergroup ID
    
    print("Initializing Bot API Client...")
    client = BotAPIClient(BASE_URL, API_SECRET)
    
    print("\n" + "="*60)
    print("LEECHING TELEGRAM FILE: https://t.me/c/3021633087/50")
    print("="*60)
    
    # First, check if bot is available
    print("\n1. Checking bot status...")
    try:
        status = client.get_status()
        if status.get('bot_available', False) and status.get('bot_status') == 'online':
            print("   ✅ Bot is online and available")
            print(f"   Active downloads: {status.get('active_downloads', 0)}")
        else:
            print("   ❌ Bot is not available")
            return
    except Exception as e:
        print(f"   Error checking status: {e}")
        return
    
    # Now, leech the specific Telegram file using full command
    print("\n2. Starting leech task for Telegram file...")
    print("   File URL: https://t.me/c/3021633087/50")
    
    try:
        # Method 1: Using full command (recommended for Telegram files)
        result = client.start_leech(
            command="/leech https://t.me/c/3021633087/50",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        
        print(f"   Leech command sent: {result.get('status', 'unknown')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        else:
            print(f"   Task ID: {result.get('task_id', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Telegram command executed: {result.get('telegram_command', 'N/A')}")
            
            # If successful, wait a moment and check downloads
            print("\n3. Checking download status...")
            time.sleep(5)  # Wait a bit for the download to start
            
            try:
                downloads = client.get_downloads()
                if 'error' in downloads:
                    print(f"   Error getting downloads: {downloads['error']}")
                else:
                    count = downloads.get('count', 0)
                    if count > 0:
                        print(f"   ✅ Found {count} active download(s):")
                        for download in downloads.get('downloads', []):
                            name = download.get('name', 'Unknown')
                            progress = download.get('progress', '0%')
                            speed = download.get('speed', '0 B/s')
                            print(f"     - {name}: {progress} at {speed}")
                    else:
                        print("   ⏳ No active downloads yet. The task may still be initializing.")
                        
            except Exception as e:
                print(f"   Error checking downloads: {e}")
                
    except Exception as e:
        print(f"   Error starting leech: {e}")
        return
    
    print("\n" + "="*60)
    print("LEECH TASK INITIATED SUCCESSFULLY")
    print("="*60)
    print("\n💡 Next steps:")
    print("   - The bot will process the leech task in the background")
    print("   - Check the bot's Telegram chat for progress updates")
    print("   - Use get_downloads() to check active tasks")
    print("   - Use get_status() to check bot health")

def leech_with_custom_name():
    """Alternative method using URL with custom name"""
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    USER_ID = "7859877609"
    CHAT_ID = "-1002934661749"
    
    client = BotAPIClient(BASE_URL, API_SECRET)
    
    print("\n" + "="*60)
    print("LEECHING WITH CUSTOM NAME")
    print("="*60)
    
    try:
        result = client.start_leech(
            url="https://t.me/c/3021633087/50",
            custom_name="telegram_file_50.mp4",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        
        print(f"Leech result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Telegram File Leecher")
    print("Choose an option:")
    print("1. Leech Telegram file with full command")
    print("2. Leech with custom name")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        leech_telegram_file()
    elif choice == "2":
        leech_with_custom_name()
    else:
        print("Invalid choice. Running default method...")
        leech_telegram_file()