#!/usr/bin/env python3
"""
Simple Leech Example - Demonstrating the simplified leech client interface
"""

from leech_client import LeechAPIClient

def main():
    """Simple example showing the two-parameter interface"""
    # Initialize client
    client = LeechAPIClient(
        base_url="http://139.162.28.139:7392",
        api_secret="wzmlx_bot_api_secret_2025"
    )
    
    # Check if bot is available
    if not client.is_bot_available():
        print("❌ Bot is not available!")
        return
    
    print("✅ Bot is ready!")
    
    # Example 1: Leech with just file parameter (using default command "/leech")
    print("\n1. Leeching with default command:")
    result = client.leech(file="https://t.me/c/3021633087/50")
    
    if result.get('status') == 'success':
        print(f"   ✅ Task submitted: {result.get('task_id')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Example 2: Leech with custom command
    print("\n2. Leeching with custom command:")
    result = client.leech(
        file="https://httpbin.org/uuid",
        command="/leech1"
    )
    
    if result.get('status') == 'success':
        print(f"   ✅ Task submitted: {result.get('task_id')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Example 3: Check status
    print("\n3. Current downloads:")
    downloads = client.get_task_status()
    if downloads.get('status') == 'success':
        count = downloads.get('count', 0)
        print(f"   Active downloads: {count}")
        for download in downloads.get('downloads', []):
            name = download.get('name', 'Unknown')
            progress = download.get('progress', '0%')
            print(f"   📄 {name}: {progress}")
    
    print("\n✨ Simple leech example completed!")

if __name__ == "__main__":
    main()