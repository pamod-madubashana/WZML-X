#!/usr/bin/env python3
"""
Test script to leech the specific Telegram file: https://t.me/c/3021633087/50
"""

import time
from bot_api_client import BotAPIClient

def main():
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    USER_ID = "7859877609"
    CHAT_ID = "-1002934661749"
    
    print("Initializing Bot API Client...")
    client = BotAPIClient(BASE_URL, API_SECRET)
    
    print("\n1. Testing bot status...")
    try:
        status = client.get_status()
        print(f"   Status: {status}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    print("\n2. Testing leech functionality...")
    print("   Leeching Telegram file: https://t.me/c/3021633087/50")
    
    try:
        # Using the full command method
        result = client.start_leech(
            command="/leech https://t.me/c/3021633087/50",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        
        print(f"   Result: {result}")
        
        if 'error' not in result:
            print("   ✅ Leech command sent successfully!")
            print("   Check the bot's Telegram chat for progress updates.")
        else:
            print(f"   ❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    print("\n3. Testing downloads endpoint...")
    try:
        downloads = client.get_downloads()
        print(f"   Downloads: {downloads}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    main()