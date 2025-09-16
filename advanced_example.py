#!/usr/bin/env python3
"""
Advanced example of using the BotAPIClient with proper error handling
"""

import json
from bot_api_client import BotAPIClient

class BotController:
    """Advanced controller for the Telegram Mirror Bot"""
    
    def __init__(self, base_url: str, api_secret: str, user_id: str):
        """
        Initialize the Bot Controller
        
        Args:
            base_url (str): Base URL of the bot API
            api_secret (str): Shared secret key for HMAC authentication
            user_id (str): User ID for executing commands
        """
        self.client = BotAPIClient(base_url, api_secret)
        self.user_id = user_id
        
    def check_bot_status(self) -> bool:
        """
        Check if the bot is online and available
        
        Returns:
            bool: True if bot is available, False otherwise
        """
        try:
            status = self.client.get_status()
            return status.get('bot_available', False) and status.get('bot_status') == 'online'
        except Exception as e:
            print(f"Error checking bot status: {e}")
            return False
            
    def get_active_downloads(self) -> dict:
        """
        Get information about active downloads
        
        Returns:
            dict: Downloads information
        """
        try:
            return self.client.get_downloads()
        except Exception as e:
            return {"error": f"Failed to get downloads: {e}"}
            
    def mirror_file(self, url: str, chat_id: str = None) -> dict:
        """
        Mirror a file to cloud storage
        
        Args:
            url (str): URL of the file to mirror
            chat_id (str, optional): Chat ID to send notifications to
            
        Returns:
            dict: Result of the mirror operation
        """
        try:
            return self.client.start_mirror(url, self.user_id, chat_id)
        except Exception as e:
            return {"error": f"Failed to start mirror: {e}"}
            
    def leech_file(self, source: str, custom_name: str = None, chat_id: str = None) -> dict:
        """
        Leech a file to Telegram
        
        Args:
            source (str): Either a URL or a full command string
            custom_name (str, optional): Custom name for the file
            chat_id (str, optional): Chat ID to send notifications to
            
        Returns:
            dict: Result of the leech operation
        """
        try:
            # If source starts with '/', treat it as a full command
            if source.startswith('/'):
                return self.client.start_leech(command=source, user_id=self.user_id, chat_id=chat_id)
            else:
                # Otherwise treat it as a URL
                return self.client.start_leech(url=source, custom_name=custom_name, 
                                            user_id=self.user_id, chat_id=chat_id)
        except Exception as e:
            return {"error": f"Failed to start leech: {e}"}
            
    def print_formatted_response(self, title: str, response: dict):
        """
        Print a formatted response
        
        Args:
            title (str): Title for the response
            response (dict): Response to print
        """
        print(f"\n{title}:")
        print("-" * len(title))
        print(json.dumps(response, indent=2))


def main():
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    
    # Initialize controller
    bot = BotController(BASE_URL, API_SECRET, USER_ID)
    
    print("Telegram Mirror Bot Controller")
    print("=" * 40)
    
    # Check if bot is available
    if bot.check_bot_status():
        print("✅ Bot is online and available")
    else:
        print("❌ Bot is not available")
        return
    
    # Get bot status details
    status = bot.client.get_status()
    bot.print_formatted_response("Bot Status", status)
    
    # Get active downloads
    downloads = bot.get_active_downloads()
    bot.print_formatted_response("Active Downloads", downloads)
    
    # Example of how to mirror a file (commented out to prevent accidental execution)
    # mirror_result = bot.mirror_file("https://example.com/file.zip")
    # bot.print_formatted_response("Mirror Result", mirror_result)
    
    # Example of how to leech a file with URL (commented out to prevent accidental execution)
    # leech_result = bot.leech_file("https://example.com/file.zip", "MyFile.zip")
    # bot.print_formatted_response("Leech Result", leech_result)
    
    # Example of how to leech a file with full command (commented out to prevent accidental execution)
    # leech_result = bot.leech_file("/leech https://example.com/file.zip -n MyFile.zip")
    # bot.print_formatted_response("Leech Command Result", leech_result)
    
    print("\n💡 Usage Examples:")
    print("   To mirror a file:")
    print("   bot.mirror_file('https://example.com/file.zip')")
    print("\n   To leech a file with custom name:")
    print("   bot.leech_file('https://example.com/file.zip', 'MyFile.zip')")
    print("\n   To leech with a full command:")
    print("   bot.leech_file('/leech https://example.com/file.zip -n MyFile.zip')")


if __name__ == "__main__":
    main()