#!/usr/bin/env python3
"""
Example Leech Script - Demonstrating the simplified two-parameter interface
"""

from leech_client import LeechAPIClient

def main():
    """Example showing the simple two-parameter interface"""
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
    
    # Example 1: Simple two-parameter usage (file only, uses default command)
    print("\n1. Leeching with just file parameter:")
    result = client.leech(file="https://t.me/c/3021633087/50")
    
    if result.get('status') == 'success':
        print(f"   ✅ Task submitted: {result.get('task_id')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Example 2: Two-parameter usage with custom command
    print("\n2. Leeching with file and custom command:")
    result = client.leech(
        file="https://t.me/c/3021633087/50",
        command="/leech1"
    )
    
    if result.get('status') == 'success':
        print(f"   ✅ Task submitted: {result.get('task_id')}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    print("\n✨ Example completed!")

if __name__ == "__main__":
    main()