#!/usr/bin/env python3
"""
Debug script to test signature generation
"""

import hmac
import hashlib
import json
import requests

def generate_signature(api_secret: str, body: bytes) -> str:
    """Generate HMAC-SHA256 signature"""
    return hmac.new(
        api_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

def test_signature():
    """Test signature generation and API call"""
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    
    # Test GET request (empty body)
    print("Testing GET request signature...")
    body = b''
    signature = generate_signature(API_SECRET, body)
    print(f"Generated signature: {signature}")
    
    # Make the actual API call
    url = f"{BASE_URL}/api/status"
    headers = {
        'Content-Type': 'application/json',
        'X-Bot-Signature': signature
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test POST request (with data)
    print("\nTesting POST request signature...")
    data = {"command": "/leech https://t.me/c/3021633087/50"}
    body = json.dumps(data).encode()
    signature = generate_signature(API_SECRET, body)
    print(f"Generated signature: {signature}")
    
    # Make the actual API call
    url = f"{BASE_URL}/api/leech"
    headers = {
        'Content-Type': 'application/json',
        'X-Bot-Signature': signature
    }
    
    try:
        response = requests.post(url, headers=headers, data=body)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signature()