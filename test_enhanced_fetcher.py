from src.course_path_generator.youtube_fetcher_enhanced import search_youtube_videos_enhanced

print("Testing enhanced YouTube fetcher...")

try:
    videos = search_youtube_videos_enhanced("python basics", "programming")
    print(f"Found {len(videos)} videos")
    
    for i, video in enumerate(videos[:3]):
        print(f"{i+1}. {video.get('title', 'No title')} - {video.get('duration', 'Unknown')}s")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()