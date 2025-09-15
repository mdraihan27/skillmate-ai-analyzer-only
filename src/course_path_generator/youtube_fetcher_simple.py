import yt_dlp
import json
import time
import random
from typing import List, Dict, Any


def search_youtube_videos_simple(topic: str, subject: str = "", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Simple and safe YouTube video search using yt-dlp
    """
    
    # Create search query
    if subject and subject.strip():
        search_query = f"{subject.strip()}: {topic}"
    else:
        search_query = topic
    
    search_url = f"ytsearch{max_results}:{search_query}"
    videos_info = []
    
    # Minimal configuration to avoid format issues
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Only basic info, no format processing
        'skip_download': True,
        'ignoreerrors': True,
        'socket_timeout': 10,  # Short timeout
        'retries': 1,  # Minimal retries
    }
    
    try:
        print(f"    Searching with simple yt-dlp...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_url, download=False)
            
            if 'entries' in search_results and search_results['entries']:
                for video in search_results['entries']:
                    if video and 'id' in video:
                        video_info = {
                            'video_id': video.get('id', 'N/A'),
                            'title': video.get('title', 'No Title'),
                            'url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                            'description': video.get('description', 'No description available'),
                            'duration': video.get('duration_string', 'N/A'),
                            'view_count': video.get('view_count', 0),
                            'uploader': video.get('uploader', 'Unknown'),
                            'upload_date': video.get('upload_date', 'N/A'),
                            'channel_id': video.get('channel_id', 'N/A'),
                            'channel_url': video.get('channel_url', 'N/A'),
                            'subtitles': {},  # Skip subtitles for now
                            'topic': topic
                        }
                        videos_info.append(video_info)
                
                print(f"    ✅ Successfully found {len(videos_info)} videos")
                return videos_info
            else:
                print(f"    ⚠️ No videos found in search results")
                return []
                
    except Exception as e:
        print(f"    ❌ Error during search: {str(e)}")
        return []


def get_youtube_videos_simple(topics: List[str], subject: str = "") -> List[Dict[str, Any]]:
    """
    Get YouTube videos for multiple topics using simple approach
    """
    all_topics_data = []
    
    print(f"Processing {len(topics)} topics with simple search...")
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] Searching for: '{topic}'")
        
        try:
            # Search for videos
            videos_for_topic = search_youtube_videos_simple(topic, subject)
            
            if videos_for_topic:
                topic_data = {
                    'topic': topic,
                    'videos': videos_for_topic,
                    'video_count': len(videos_for_topic)
                }
                all_topics_data.append(topic_data)
                print(f"  ✓ Found {len(videos_for_topic)} videos for '{topic}'")
            else:
                print(f"  ✗ No videos found for '{topic}'")
                # Add empty topic data
                topic_data = {
                    'topic': topic,
                    'videos': [],
                    'video_count': 0
                }
                all_topics_data.append(topic_data)
            
            # Add a small delay between requests
            if i < len(topics):
                time.sleep(1)
                
        except Exception as e:
            print(f"  ❌ Error processing topic '{topic}': {str(e)}")
            # Add empty topic data for failed topics
            topic_data = {
                'topic': topic,
                'videos': [],
                'video_count': 0
            }
            all_topics_data.append(topic_data)
    
    total_videos = sum(topic_data['video_count'] for topic_data in all_topics_data)
    print(f"\n✅ Simple search completed! Found {total_videos} videos across {len(all_topics_data)} topics")
    
    return all_topics_data


if __name__ == "__main__":
    # Test the simple approach
    test_topics = ["Python basics", "Variables in Python"]
    result = get_youtube_videos_simple(test_topics, "Python Programming")
    
    print(f"\nTest Results:")
    for topic_data in result:
        print(f"Topic: {topic_data['topic']}")
        print(f"Videos found: {topic_data['video_count']}")
        for video in topic_data['videos'][:2]:  # Show first 2 videos
            print(f"  - {video['title']}")