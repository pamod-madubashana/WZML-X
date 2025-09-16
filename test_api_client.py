#!/usr/bin/env python3
"""
Test API Client - Simple script to verify the Perfect Bot API Client works correctly
"""

from perfect_bot_api_client import PerfectBotAPIClient

def test_api_client():
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    
    print("Testing Perfect Bot API Client...")
    
    # Initialize client
    client = PerfectBotAPIClient(BASE_URL, API_SECRET)
    
    # Test 1: Get help (no auth required)
    print("\n1. Testing help endpoint (no auth required)...")
    help_info = client.get_help()
    if "error" not in help_info:
        print("   ✅ Help endpoint working")
        print(f"   API Version: {help_info.get('api_version')}")
    else:
        print(f"   ❌ Help endpoint error: {help_info.get('error')}")
        return
    
    # Test 2: Get status (auth required)
    print("\n2. Testing status endpoint (auth required)...")
    status = client.get_status()
    print(f"   Status response: {status}")
    if status.get('status') == 'success':
        print("   ✅ Status endpoint working")
        print(f"   Bot status: {status.get('bot_status')}")
    else:
        print(f"   ⚠️  Status endpoint issue: {status.get('error', 'Unknown error')}")
    
    # Test 3: Get downloads (auth required)
    print("\n3. Testing downloads endpoint (auth required)...")
    downloads = client.get_downloads()
    print(f"   Downloads response: {downloads}")
    if downloads.get('status') == 'success':
        print("   ✅ Downloads endpoint working")
        print(f"   Active downloads: {downloads.get('count')}")
    else:
        print(f"   ⚠️  Downloads endpoint issue: {downloads.get('error', 'Unknown error')}")
    
    # Test 4: Try to submit a leech task (auth required)
    print("\n4. Testing leech endpoint (auth required)...")
    leech_result = client.start_leech(
        command="/leech https://httpbin.org/uuid",
        user_id="7859877609",
        chat_id="-1002934661749"
    )
    print(f"   Leech response: {leech_result}")
    if leech_result.get('status') == 'success':
        print("   ✅ Leech endpoint working")
        print(f"   Task ID: {leech_result.get('task_id')}")
    else:
        print(f"   ⚠️  Leech endpoint issue: {leech_result.get('error', 'Unknown error')}")
    
    print("\n✅ API client test completed!")

if __name__ == "__main__":
    test_api_client()