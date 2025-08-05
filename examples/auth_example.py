"""Example script demonstrating how to authenticate with the Legal RAG API"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL - change this to match your deployment
API_BASE_URL = "http://localhost:8000"

# Admin credentials - in production, these should be securely stored
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

def get_auth_token():
    """Get an authentication token from the API"""
    token_url = f"{API_BASE_URL}/admin/token"
    
    # Prepare the form data for token request
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    # Send the token request
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Failed to get token: {response.status_code}")
        print(response.text)
        return None

def make_authenticated_request(endpoint, method="GET", data=None):
    """Make an authenticated request to the API"""
    # Get the authentication token
    token = get_auth_token()
    
    if not token:
        return None
    
    # Prepare the headers with the token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Add content type header if sending data
    if data:
        headers["Content-Type"] = "application/json"
    
    # Prepare the full URL
    url = f"{API_BASE_URL}{endpoint}"
    
    # Make the request
    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method.upper() == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        print(f"Unsupported method: {method}")
        return None
    
    # Return the response
    return response

def main():
    """Main function to demonstrate API authentication"""
    # Example 1: Get system stats (authenticated endpoint)
    stats_response = make_authenticated_request("/admin/stats")
    
    if stats_response:
        print("\nSystem Stats:")
        print(json.dumps(stats_response.json(), indent=2))
    
    # Example 2: Get system configuration (authenticated endpoint)
    config_response = make_authenticated_request("/admin/config")
    
    if config_response:
        print("\nSystem Configuration:")
        print(json.dumps(config_response.json(), indent=2))
    
    # Example 3: Health check (public endpoint, no authentication required)
    health_response = requests.get(f"{API_BASE_URL}/admin/health")
    
    print("\nHealth Check (Public Endpoint):")
    print(json.dumps(health_response.json(), indent=2))

if __name__ == "__main__":
    main()