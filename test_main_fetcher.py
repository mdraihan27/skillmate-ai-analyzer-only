from src.course_path_generator.get_youtube_videos import get_youtube_videos_for_topics

print("Testing main YouTube video fetcher...")

try:
    topics = ["Python basics", "Variables in Python"]
    result = get_youtube_videos_for_topics(topics, "Programming")
    
    print(f"Processed {len(result)} topics")
    
    for topic_data in result:
        print(f"\nTopic: {topic_data['topic_name']}")
        print(f"Found {topic_data['video_count']} videos")
        
        for i, video in enumerate(topic_data['videos'][:2]):  # Show first 2 videos
            print(f"  {i+1}. {video.get('title', 'No title')} - {video.get('duration', 'Unknown')}s")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()