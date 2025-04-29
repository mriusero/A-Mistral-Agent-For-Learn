import os
import requests
from dotenv import load_dotenv
from isodate import parse_duration

def extract_video_id(video_url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    """
    return video_url.split('v=')[-1]

def get_text(video_id: str, api_key: str) -> dict:
    """
    Use YouTube API to get video details.
    """
    youtube_url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={api_key}'
    youtube_response = requests.get(youtube_url)
    youtube_data = youtube_response.json()

    if 'items' in youtube_data and len(youtube_data['items']) > 0:
        snippet = youtube_data['items'][0]['snippet']
        content_details = youtube_data['items'][0]['contentDetails']
        duration = parse_duration(content_details['duration']).total_seconds()
        return {
            'title': snippet['title'],
            'description': snippet['description'],
            'duration': duration
        }
    else:
        raise Exception("Impossible to retrieve video details. Please check the video ID or API key.")

def get_visual() -> dict:
    """
    Use Youtube API to get visual analysis of the video.
    """
    return {
        'visual_analysis': 'Empty, you have to find another source to get more data about this video.'
    }

def analyze_youtube_video(video_url: str) -> dict:
    """
    Analyse the text description and the visual content of a Youtube video.
    Args:
        video_url (str): The URL of the YouTube video to analyze.
    """
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')

    video_id = extract_video_id(video_url)
    text_details = get_text(video_id, api_key)
    video_details = get_visual()

    try:
        result = f"Title: {text_details['title']}"
        result += f"\nDescription: {text_details['description']}"
        result += f"\nDuration: {text_details['duration']} seconds"
        result += f"\nVisual Analysis: {video_details['visual_analysis']}"
        return result
    except Exception as e:
        return e