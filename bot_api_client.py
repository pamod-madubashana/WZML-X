#!/usr/bin/env python3
"""
Fully functional client API for communicating with the Telegram Mirror Bot API.
This client includes all necessary functions to interact with the bot's API endpoints
and comprehensive test functions.
"""

import hmac
import hashlib
import json
import requests
from time import time
from typing import Dict, Any, Optional

class BotAPIClient:
    """Client for interacting with the Telegram Mirror Bot API"""
    
    def __init__(self, base_url: str, api_secret: str):
        """
        Initialize the Bot API Client
        
        Args:
            base_url (str): Base URL of the bot API (e.g., 'http://139.162.28.139:7392')
            api_secret (str): Shared secret key for HMAC authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_secret = api_secret
        self.session = requests.Session()
        
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
            endpoint (str): API endpoint (e.g., '/api/status')
            data (dict, optional): Request data for POST requests
            
        Returns:
            dict: JSON response from the API
        """
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if data is not None:
            body = json.dumps(data).encode()
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
        
    def get_status(self) -> Dict:
        """
        Get bot status information
        
        Returns:
            dict: Bot status information
        """
        return self._make_request('GET', '/api/status')
        
    def get_downloads(self) -> Dict:
        """
        Get list of current downloads
        
        Returns:
            dict: Current downloads information
        """
        return self._make_request('GET', '/api/downloads')
        
    def start_mirror(self, url: str, user_id: Optional[str] = None, chat_id: Optional[str] = None) -> Dict:
        """
        Start a mirror task
        
        Args:
            url (str): URL to mirror
            user_id (str, optional): User ID for the task
            chat_id (str, optional): Chat ID for the task
            
        Returns:
            dict: Response from the API
        """
        data = {"url": url}
        if user_id:
            data["user_id"] = user_id
        if chat_id:
            data["chat_id"] = chat_id
            
        return self._make_request('POST', '/api/mirror', data)
        
    def start_leech(self, command: Optional[str] = None, url: Optional[str] = None, 
                   custom_name: Optional[str] = None, user_id: Optional[str] = None, 
                   chat_id: Optional[str] = None) -> Dict:
        """
        Start a leech task
        
        Args:
            command (str, optional): Full leech command text
            url (str, optional): URL to leech (legacy mode)
            custom_name (str, optional): Custom filename (with url)
            user_id (str, optional): User ID for the task
            chat_id (str, optional): Chat ID for the task
            
        Returns:
            dict: Response from the API
        """
        data = {}
        
        if command:
            data["command"] = command
        elif url:
            data["url"] = url
            if custom_name:
                data["custom_name"] = custom_name
        else:
            return {"error": "Either 'command' or 'url' must be provided"}
            
        if user_id:
            data["user_id"] = user_id
        if chat_id:
            data["chat_id"] = chat_id
            
        return self._make_request('POST', '/api/leech', data)
        
    def get_help(self) -> Dict:
        """
        Get API documentation
        
        Returns:
            dict: API documentation
        """
        # Help endpoint doesn't require authentication
        url = f"{self.base_url}/api/help"
        response = self.session.get(url)
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON response: {response.text}", "status_code": response.status_code}


def test_bot_api_client():
    """
    Test functions for the BotAPIClient
    """
    # Configuration - Update these values as needed
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    CHAT_ID = "-1002934661749"  # Default chat ID used by the bot
    
    print("Initializing Bot API Client...")
    client = BotAPIClient(BASE_URL, API_SECRET)
    
    print("\n" + "="*50)
    print("BOT API CLIENT TESTS")
    print("="*50)
    
    # Test 1: Get API Help
    print("\n1. Testing API Help Endpoint:")
    try:
        help_info = client.get_help()
        print(f"   API Version: {help_info.get('api_version', 'Unknown')}")
        print(f"   Description: {help_info.get('description', 'N/A')}")
        print(f"   Endpoints: {list(help_info.get('endpoints', {}).keys())}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Get Bot Status
    print("\n2. Testing Bot Status:")
    try:
        status = client.get_status()
        if "error" in status:
            print(f"   Error: {status['error']}")
        else:
            print(f"   Bot Status: {status.get('bot_status', 'Unknown')}")
            print(f"   Active Downloads: {status.get('active_downloads', 0)}")
            print(f"   Bot Available: {status.get('bot_available', False)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Get Downloads
    print("\n3. Testing Downloads Endpoint:")
    try:
        downloads = client.get_downloads()
        if "error" in downloads:
            print(f"   Error: {downloads['error']}")
        else:
            print(f"   Downloads Response: {downloads}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Start Mirror Task (Example)
    print("\n4. Testing Mirror Task (Example - will fail without valid URL):")
    try:
        # This is just an example - you would use a real URL in practice
        result = client.start_mirror(
            url="https://example.com/file.zip",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        if "error" in result:
            print(f"   Expected Error: {result['error']}")
        else:
            print(f"   Mirror Task Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Start Leech Task (Example)
    print("\n5. Testing Leech Task (Example - will fail without valid URL):")
    try:
        # This is just an example - you would use a real command in practice
        result = client.start_leech(
            command="/leech https://example.com/file.zip",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        if "error" in result:
            print(f"   Expected Error: {result['error']}")
        else:
            print(f"   Leech Task Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Start Leech Task with URL (Example)
    print("\n6. Testing Leech Task with URL (Example - will fail without valid URL):")
    try:
        # This is just an example - you would use a real URL in practice
        result = client.start_leech(
            url="https://example.com/file.zip",
            custom_name="MyFile.zip",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        if "error" in result:
            print(f"   Expected Error: {result['error']}")
        else:
            print(f"   Leech Task Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*50)
    print("BOT API CLIENT TESTS COMPLETED")
    print("="*50)


if __name__ == "__main__":
    test_bot_api_client()