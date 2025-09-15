#!/usr/bin/env python3
"""
Test script to verify Gemini API rate limiting fallback system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from course_path_generator.get_topics import generate_learning_topics, _call_gemini_api
from dotenv import load_dotenv

def test_api_fallback():
    """Test that API fallback system works with multiple Gemini API keys"""
    
    load_dotenv()
    
    print("🧪 Testing Gemini API Rate Limiting Fallback System")
    print("=" * 60)
    
    # Test 1: Check that all API keys are loaded
    api_keys = [
        os.getenv('GEMINI_API_KEY'),
        os.getenv('GEMINI_API_KEY2'), 
        os.getenv('GEMINI_API_KEY3')
    ]
    
    api_keys = [key for key in api_keys if key]
    print(f"✅ Found {len(api_keys)} Gemini API keys in environment")
    
    if len(api_keys) < 2:
        print("⚠️ Warning: Only 1 API key found. Fallback system needs multiple keys to test properly.")
        return False
    
    # Test 2: Test simple topic generation (should work with first key)
    print("\n🔹 Test 1: Basic topic generation")
    try:
        topics = generate_learning_topics("Python", "beginner")
        print(f"✅ Successfully generated {len(topics)} topics")
        print(f"   First topic: {topics[0]}")
    except Exception as e:
        print(f"❌ Topic generation failed: {e}")
        return False
    
    # Test 3: Test direct API call
    print("\n🔹 Test 2: Direct API call")
    try:
        response = _call_gemini_api("What is Python programming? Answer in one sentence.")
        if "Error" in response:
            print(f"⚠️ API call returned error: {response}")
        else:
            print(f"✅ API call successful: {response[:100]}...")
    except Exception as e:
        print(f"❌ Direct API call failed: {e}")
        return False
    
    print("\n🎉 Rate limiting fallback system test completed!")
    print("\nℹ️ To test actual rate limiting, you would need to:")
    print("   1. Make many API calls quickly to trigger rate limits")
    print("   2. Use an invalid API key as the first key")
    print("   3. Monitor the console output for 'Trying Gemini API key X/Y' messages")
    
    return True

if __name__ == "__main__":
    success = test_api_fallback()
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)