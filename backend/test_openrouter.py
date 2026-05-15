"""
Quick script to test OpenRouter API connectivity
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_service import test_ai_connection

if __name__ == "__main__":
    print("Testing OpenRouter API connectivity...")
    print(f"API Key present: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    print()
    
    result = test_ai_connection()
    
    print(f"Status: {result['status']}")
    print(f"Model: {result['model']}")
    
    if result['status'] == 'success':
        print(f"Response: {result['response']}")
        print("\n✓ OpenRouter API connection successful!")
    else:
        print(f"Error: {result['error']}")
        print("\n✗ OpenRouter API connection failed!")

# Made with Bob
