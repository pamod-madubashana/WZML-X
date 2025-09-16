#!/usr/bin/env python3
"""
Example usage of the BotAPIClient
"""

from bot_api_client import BotAPIClient

def main():
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    
    # Initialize the client
    client = BotAPIClient(BASE_URL, API_SECRET)
    
    # Get bot status
    print("Getting bot status...")
    status = client.get_status()
    print(f"Status: {status}")
    
    # Get current downloads
    print("\nGetting current downloads...")
    downloads = client.get_downloads()
    print(f"Downloads: {downloads}")
    
    # Start a mirror task (example)
    print("\nStarting mirror task...")
    result = client.start_mirror(
        url="https://example.com/file.zip",
        user_id=USER_ID
    )
    print(f"Mirror result: {result}")
    
    # Start a leech task with full command
    print("\nStarting leech task...")
    result = client.start_leech(
        command="/leech https://example.com/file.zip -n MyFile.zip",
        user_id=USER_ID
    )
    print(f"Leech result: {result}")

if __name__ == "__main__":
    main()