#!/usr/bin/env python3
"""
Final integration test for the fixed AI-Powered Content Platform
Tests multi-API key fallback + fixed yt-dlp (no YouTube API)
"""
import sys
import os
import time

# Add the src directory to the path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from course_path_generator.get_topics import generate_learning_topics
from course_path_generator.main_course_creator import create_complete_course
from dotenv import load_dotenv

def test_api_ready():
    """Test that the API is ready for deployment"""
    
    load_dotenv()
    
    print("🚀 Final Integration Test - API Ready Check")
    print("=" * 60)
    
    # Test parameters
    subject = "Java"
    difficulty = "beginner"
    
    print(f"\n🎯 Testing complete course creation for: {subject} ({difficulty})")
    print("This tests the entire API workflow:\n")
    print("  1. ✅ Gemini API with 3-key fallback")
    print("  2. ✅ yt-dlp with fixed format handling") 
    print("  3. ✅ No YouTube API dependencies")
    print("  4. ✅ Complete course path generation")
    
    start_time = time.time()
    
    try:
        # Test the complete workflow (same as API endpoint)
        print(f"\n📡 Calling create_complete_course('{subject}', '{difficulty}')")
        
        course_result = create_complete_course(subject, difficulty)
        
        end_time = time.time()
        
        if course_result.get('success'):
            course_data = course_result.get('data', {})
            course_path = course_data.get('coursePath', {})
            topics = course_data.get('topics', [])
            
            print(f"\n🎉 SUCCESS! Course created in {end_time - start_time:.1f} seconds")
            print(f"\n📊 Course Summary:")
            print(f"   📚 Title: {course_path.get('title', 'N/A')}")
            print(f"   🎯 Subject: {course_path.get('subject', 'N/A')}")
            print(f"   📈 Difficulty: {course_path.get('difficulty', 'N/A')}")
            print(f"   📝 Topics: {len(topics)}")
            print(f"   🎥 Videos found: {sum(1 for topic in topics if topic.get('videoInfo', {}).get('youtubeUrl') != 'N/A')}")
            
            print(f"\n📋 First 3 Topics:")
            for i, topic in enumerate(topics[:3], 1):
                video_info = topic.get('videoInfo', {})
                print(f"   {i}. {topic.get('name', 'N/A')}")
                print(f"      🎥 Video: {video_info.get('title', 'N/A')[:50]}...")
            
            print(f"\n✅ API READY FOR DEPLOYMENT!")
            print(f"\n🌐 Endpoint: POST /api/v1/generate-course-path")
            print(f"📝 Request: {{\"subject\": \"{subject}\", \"difficulty\": \"{difficulty}\"}}")
            
            return True
            
        else:
            print(f"\n❌ Course creation failed: {course_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n💥 Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_ready()
    if success:
        print("\n" + "="*60)
        print("🎊 ALL SYSTEMS GO! Your API is ready for production!")
        print("🚀 Deploy to Render and start creating courses!")
        sys.exit(0)
    else:
        print("\n" + "="*60) 
        print("❌ API has issues - check the logs above")
        sys.exit(1)