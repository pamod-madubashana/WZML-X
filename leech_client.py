#!/usr/bin/env python3
"""
Leech Client - Dedicated API client for leeching Telegram files via the Mirror Bot API
This client provides focused functionality for leeching files with proper authentication
and error handling specifically for Telegram file operations.
"""

import hmac
import hashlib
import json
import requests
from time import time
from typing import Dict, Optional

class LeechAPIClient:
    """Dedicated client for leeching Telegram files via the Mirror Bot API"""
    
    def __init__(self, base_url: str, api_secret: str):
        """
        Initialize the Leech API Client
        
        Args:
            base_url (str): Base URL of the bot API (e.g., 'http://139.162.28.139:7392')
            api_secret (str): Shared secret key for HMAC authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def _generate_signature(self, body: bytes) -> str:
        """
        Generate HMAC-SHA256 signature for API requests
        
        Args:
            body (bytes): Request body as bytes
            
        Returns:
            str: Hex digest of the HMAC signature
        """
        return hmac.new(
            self.api_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to the bot API
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint (e.g., '/api/leech')
            data (dict, optional): Request data for POST requests
            
        Returns:
            dict: JSON response from the API
        """
        url = f"{self.base_url}{endpoint}"
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Handle request body and signature
        if data is not None:
            body = json.dumps(data, separators=(',', ':')).encode()
            headers['X-Bot-Signature'] = self._generate_signature(body)
            response = self.session.request(method, url, headers=headers, data=body)
        else:
            # For GET requests, body is empty
            headers['X-Bot-Signature'] = self._generate_signature(b'')
            response = self.session.request(method, url, headers=headers)
            
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON response: {response.text}", "status_code": response.status_code}
    
    def leech(self, file: str, command: str = "/leech", user_id: str = "7859877609", 
              chat_id: str = "-1002934661749") -> Dict:
        """
        Leeche a file (Telegram link or other URL) with a custom command
        
        Args:
            file (str): File URL (Telegram link or HTTP URL)
            command (str): Leech command (default: "/leech")
            user_id (str): User ID for the task (default: Pamod's ID)
            chat_id (str): Chat ID for the task (default: supergroup)
            
        Returns:
            dict: Response from the API with task information
        """
        # Create the full command
        full_command = f"{command} {file}"
            
        # Prepare request data
        data = {
            "command": full_command,
            "user_id": user_id,
            "chat_id": chat_id
        }
        
        # Make the API request
        return self._make_request('POST', '/api/leech', data)
    
    def get_task_status(self, task_id: Optional[str] = None) -> Dict:
        """
        Get the status of leech tasks or all current downloads
        
        Args:
            task_id (str, optional): Specific task ID to check
            
        Returns:
            dict: Downloads information from the API
        """
        return self._make_request('GET', '/api/downloads')
    
    def get_bot_status(self) -> Dict:
        """
        Get overall bot status
        
        Returns:
            dict: Bot status information
        """
        return self._make_request('GET', '/api/status')
    
    def is_bot_available(self) -> bool:
        """
        Check if the bot is available and responding
        
        Returns:
            bool: True if bot is available, False otherwise
        """
        try:
            response = self.get_bot_status()
            return response.get('status') == 'success' and response.get('bot_available', False)
        except:
            return False


def main():
    """Main function demonstrating leech client usage"""
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Pamod's user ID
    CHAT_ID = "-1002934661749"  # Supergroup ID
    
    # Initialize client
    print("🚀 Initializing Leech API Client...")
    client = LeechAPIClient(BASE_URL, API_SECRET)
    
    # Check if bot is available
    if not client.is_bot_available():
        print("❌ Bot is not available!")
        return
    
    print("✅ Bot is available and ready for leeching!")
    
    # Get bot status
    status = client.get_bot_status()
    print(f"📊 Bot Status: {status.get('bot_status', 'Unknown')}")
    print(f"   Active Downloads: {status.get('active_downloads', 0)}")
    
    # Example 1: Leech a Telegram file (the specific one mentioned)
    print("\n⚡ Leeching Telegram File:")
    telegram_file_url = "https://t.me/c/3021633087/24"
    result = client.leech(
        file=telegram_file_url,
        command="/leech",
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if result.get('status') == 'success':
        task_id = result.get('task_id')
        print(f"   ✅ Leech task submitted successfully!")
        print(f"   Task ID: {task_id}")
        print(f"   Command: {result.get('telegram_command')}")
        print(f"   Auto Status: {result.get('auto_status')}")
    else:
        print(f"   ❌ Failed to submit leech task: {result.get('error')}")

if __name__ == "__main__":
    main()