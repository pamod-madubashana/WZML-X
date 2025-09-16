#!/usr/bin/env python3
"""
Comprehensive API Example - Shows all available functionality of the Perfect Bot API Client
"""

import time
from perfect_bot_api_client import PerfectBotAPIClient, BotTaskManager

def main():
    # Configuration - Update these values as needed
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    CHAT_ID = "-1002934661749"  # Default chat ID used by the bot
    
    # Initialize the perfect client
    print("🚀 Initializing Perfect Bot API Client...")
    client = PerfectBotAPIClient(BASE_URL, API_SECRET)
    
    # Check API availability
    print("🔍 Checking API availability...")
    if not client.is_api_available():
        print("❌ API is not available! Exiting.")
        return
    
    print(f"✅ API is available (Version: {client.get_api_version()})")
    
    # Initialize task manager
    print("📋 Initializing Task Manager...")
    task_manager = BotTaskManager(client)
    
    # Display API documentation
    print("\n📚 API Documentation:")
    help_info = client.get_help()
    if "error" not in help_info:
        print(f"   Version: {help_info.get('api_version')}")
        print(f"   Description: {help_info.get('description')}")
        print("   Endpoints:")
        for endpoint, details in help_info.get('endpoints', {}).items():
            print(f"     {endpoint} ({details.get('method')}): {details.get('description')}")
    else:
        print(f"   Error getting help: {help_info.get('error')}")
    
    # Get bot status
    print("\n📊 Bot Status:")
    status = client.get_status()
    if status.get('status') == 'success':
        print(f"   Status: {status.get('bot_status')}")
        print(f"   Active Downloads: {status.get('active_downloads')}")
        print(f"   Bot Available: {status.get('bot_available')}")
    else:
        print(f"   Error: {status.get('error')}")
    
    # Get current downloads
    print("\n📥 Current Downloads:")
    downloads = client.get_downloads()
    if downloads.get('status') == 'success':
        count = downloads.get('count', 0)
        print(f"   Active Downloads: {count}")
        for download in downloads.get('downloads', []):
            print(f"     📄 {download.get('name')}")
            print(f"        Progress: {download.get('progress')}")
            print(f"        Speed: {download.get('speed')}")
            print(f"        ETA: {download.get('eta')}")
            print(f"        Status: {download.get('status')}")
    else:
        print(f"   Error: {downloads.get('error')}")
    
    # Submit a leech task for a Telegram file
    print("\n⚡ Submitting Leech Task for Telegram File:")
    leech_result = client.start_leech(
        command="/leech https://t.me/c/3021633087/50",
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if leech_result.get('status') == 'success':
        print(f"   ✅ Leech task submitted successfully!")
        print(f"   Task ID: {leech_result.get('task_id')}")
        print(f"   Command: {leech_result.get('telegram_command')}")
        print(f"   Auto Status Sent: {leech_result.get('auto_status')}")
        
        # Wait a moment and check downloads
        print("\n⏳ Waiting 5 seconds and checking downloads...")
        time.sleep(5)
        
        downloads = client.get_downloads()
        if downloads.get('status') == 'success' and downloads.get('count', 0) > 0:
            print("   Current downloads after submission:")
            for download in downloads.get('downloads', []):
                print(f"     📄 {download.get('name')}: {download.get('progress')}")
        else:
            print("   No active downloads yet")
    else:
        print(f"   ❌ Failed to submit leech task: {leech_result.get('error')}")
    
    # Submit a mirror task
    print("\n🔗 Submitting Mirror Task:")
    mirror_result = client.start_mirror(
        url="https://httpbin.org/uuid",  # Small test file
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if mirror_result.get('status') == 'success':
        print(f"   ✅ Mirror task submitted successfully!")
        print(f"   Task ID: {mirror_result.get('task_id')}")
        print(f"   URL: {mirror_result.get('url')}")
    else:
        print(f"   ❌ Failed to submit mirror task: {mirror_result.get('error')}")
    
    # Demonstrate task manager usage
    print("\n🎯 Using Task Manager:")
    # Submit another leech task through task manager
    task = task_manager.submit_leech_task(
        command="/leech https://httpbin.org/uuid -n test_file.txt",
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if task:
        print(f"   Task Manager submitted task: {task.task_id}")
        print(f"   Command: {task.command}")
        
        # Check bot status through task manager
        bot_status = task_manager.get_bot_status()
        print(f"   Bot Status via Task Manager: {bot_status.get('bot_status')}")
        
        # Check downloads through task manager
        active_downloads = task_manager.get_active_downloads()
        print(f"   Active Downloads via Task Manager: {active_downloads.get('count', 0)}")
    else:
        print("   Failed to submit task through task manager")
    
    # Final status check
    print("\n🏁 Final Status Check:")
    final_status = client.get_status()
    if final_status.get('status') == 'success':
        print(f"   Bot is {final_status.get('bot_status')}")
        print(f"   Active downloads: {final_status.get('active_downloads')}")
    else:
        print(f"   Error checking final status: {final_status.get('error')}")
    
    print("\n✨ Comprehensive API example completed!")


if __name__ == "__main__":
    main()