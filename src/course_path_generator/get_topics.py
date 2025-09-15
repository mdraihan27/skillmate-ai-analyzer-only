import os
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic.v1.validators import number_size_validator

# Load environment variables from .env file
load_dotenv()

def generate_learning_topics(subject, difficulty_level):

    valid_levels = ["beginner", "intermediate", "advanced"]
    if difficulty_level.lower() not in valid_levels:
        raise ValueError(f"Difficulty level must be one of: {', '.join(valid_levels)}")

    number_of_videos =0
    if difficulty_level == "beginner":
        number_of_videos = 15
    elif difficulty_level == "intermediate":
        number_of_videos = 25
    elif difficulty_level == "advanced":
        number_of_videos = 50

    prompt = f"""You are an expert curriculum designer. Generate a comprehensive list of topics for learning {subject} at the {difficulty_level.lower()} level.

Instructions:
- Provide ONLY a numbered list of topics
- Each topic should be specific and actionable
- Topics should be ordered from foundational to more complex within the {difficulty_level.lower()} level
- For {difficulty_level.lower()} level, ensure topics are appropriate for someone at this skill level
- Do not include any explanations, introductions, or additional text
- Each line should contain only: "1. Topic Name" format
- Keep number of topics under {number_of_videos}

Subject: {subject}
Difficulty Level: {difficulty_level.capitalize()}

Topics:"""

    gemini_response = _call_gemini_api(prompt)
    
    topics = _parse_gemini_response(gemini_response)
    
    return topics


def _call_gemini_api(prompt):
    """Call Gemini API with automatic fallback to other API keys on ANY error"""
    
    # List of all available API keys (now supporting 5 keys)
    api_keys = [
        os.getenv('GEMINI_API_KEY'),
        os.getenv('GEMINI_API_KEY2'), 
        os.getenv('GEMINI_API_KEY3'),
        os.getenv('GEMINI_API_KEY4'),
        os.getenv('GEMINI_API_KEY5')
    ]
    
    # Filter out None values
    api_keys = [key for key in api_keys if key]
    
    if not api_keys:
        raise ValueError("No Gemini API keys found in environment variables")
    
    # Try each API key until successful or all fail
    for i, api_key in enumerate(api_keys):
        try:
            print(f"Trying Gemini API key {i+1}/{len(api_keys)}...")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            print(f"✅ Success with API key {i+1}")
            return response.text
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a rate limit error for specific messaging
            if any(term in error_msg for term in ['rate limit', 'quota', 'limit exceeded', 'too many requests']):
                print(f"⚠️ Rate limit hit with API key {i+1}. Trying next key...")
            else:
                # For any other error, also try next key
                print(f"⚠️ Error with API key {i+1}: {str(e)[:100]}... Trying next key...")
            
            # Continue to next key for ANY error (not just rate limits)
            if i < len(api_keys) - 1:  # Not the last key
                continue
            else:  # Last key, all failed
                return f"Error: All {len(api_keys)} Gemini API keys failed. Last error: {str(e)}"


def _parse_gemini_response(response):
    
    topics = []
    
    lines = response.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            
            topic = line.split('.', 1)[1].strip() if '.' in line else line

            topics.append(topic)
    
    return topics


# Example usage
if __name__ == "__main__":
    # Test the function
    try:
        topics = generate_learning_topics("Python Programming", "beginner")
        print(f"Learning topics for Python Programming (Beginner level):")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")
    except ValueError as e:
        print(f"Error: {e}")
