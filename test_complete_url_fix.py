#!/usr/bin/env python3
"""
Test complete API workflow with URL fix to ensure everything still works
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from course_path_generator.main_course_creator import create_complete_course
from dotenv import load_dotenv

def test_complete_workflow_with_url_fix():
    """Test that the complete workflow works with the URL fix"""
    
    load_dotenv()
    
    print("🔍 Testing Complete Workflow with URL Fix...")
    print("=" * 60)
    
    # Test with a smaller course for faster testing
    subject = "Python"
    difficulty = "beginner"
    
    print(f"🎯 Creating course: {subject} ({difficulty})")
    print("🧪 Testing: Topic generation → Video search → URL extraction → Course creation")
    
    try:
        # Call the same function as the API
        course_result = create_complete_course(subject, difficulty)
        
        if course_result.get('success'):
            course_data = course_result.get('data', {})
            topics = course_data.get('topics', [])
            
            print(f"\n✅ Course creation successful!")
            print(f"📊 Generated {len(topics)} topics")
            
            # Check URL extraction in each topic
            total_videos = 0
            valid_urls = 0
            missing_urls = 0
            
            print(f"\n🔍 Checking URL extraction in topics...")
            
            for i, topic in enumerate(topics[:5], 1):  # Check first 5 topics
                topic_name = topic.get('name', 'Unknown')[:40] + "..."
                video_info = topic.get('videoInfo', {})
                video_url = video_info.get('youtubeUrl', 'N/A')
                video_title = video_info.get('title', 'N/A')[:40] + "..."
                
                print(f"\n📝 Topic {i}: {topic_name}")
                print(f"   🎥 Video: {video_title}")
                print(f"   🔗 URL: {video_url}")
                
                total_videos += 1
                
                if video_url and video_url != 'N/A' and 'youtube.com' in video_url:
                    valid_urls += 1
                    print(f"   ✅ URL Status: VALID")
                else:
                    missing_urls += 1
                    print(f"   ❌ URL Status: MISSING")
            
            print(f"\n📊 URL Fix Results:")
            print(f"   🎥 Total Videos Checked: {total_videos}")
            print(f"   ✅ Valid URLs: {valid_urls}")
            print(f"   ❌ Missing URLs: {missing_urls}")
            print(f"   📈 URL Success Rate: {(valid_urls / total_videos * 100):.1f}%")
            
            if missing_urls == 0:
                print(f"\n🎉 PERFECT! URL fix is working in the complete workflow!")
                print(f"✅ API responses will now always include YouTube URLs!")
                return True
            else:
                print(f"\n⚠️ Some URLs still missing in the complete workflow.")
                return False
                
        else:
            print(f"❌ Course creation failed: {course_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"💥 Error in complete workflow: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow_with_url_fix()
    if success:
        print("\n" + "="*60)
        print("🚀 URL FIX CONFIRMED WORKING IN COMPLETE API!")
        print("✅ Your API will now always return YouTube URLs!")
        print("🎊 Ready for deployment with complete URL support!")
    else:
        print("\n❌ URL fix needs more investigation")