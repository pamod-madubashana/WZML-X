#!/usr/bin/env python3
"""
Test Leech Client - Simple test script for the leech client
"""

from leech_client import LeechAPIClient

def test_leech_client():
    """Test the leech client functionality"""
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    
    print("Testing Leech API Client...")
    
    # Initialize client
    client = LeechAPIClient(BASE_URL, API_SECRET)
    
    # Test 1: Check if bot is available
    print("\n1. Testing bot availability...")
    if client.is_bot_available():
        print("   ✅ Bot is available")
    else:
        print("   ❌ Bot is not available")
        return
    
    # Test 2: Get bot status
    print("\n2. Testing bot status...")
    status = client.get_bot_status()
    if status.get('status') == 'success':
        print(f"   ✅ Bot status: {status.get('bot_status')}")
        print(f"   Active downloads: {status.get('active_downloads')}")
    else:
        print(f"   ❌ Error: {status.get('error')}")
    
    # Test 3: Submit a leech task with the new interface
    print("\n3. Testing leech task submission...")
    result = client.leech(
        file="https://t.me/c/3021633087/50",
        command="/leech",
        user_id="7859877609",
        chat_id="-1002934661749"
    )
    
    if result.get('status') == 'success':
        print("   ✅ Leech task submitted successfully!")
        print(f"   Task ID: {result.get('task_id')}")
        print(f"   Command: {result.get('telegram_command')}")
    else:
        print(f"   ❌ Failed to submit leech task: {result.get('error')}")

    print("\n✅ Leech client test completed!")

if __name__ == "__main__":
    test_leech_client()