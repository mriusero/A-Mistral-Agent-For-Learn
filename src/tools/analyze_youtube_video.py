import os
import requests
from dotenv import load_dotenv
from isodate import parse_duration
from youtube_transcript_api import YouTubeTranscriptApi
from src.utils.tooling import tool

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

def get_transcript(video_id: str) -> str:
    """
    Use youtube-transcript-api to get video transcript.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript])
        return transcript_text
    except Exception as e:
        return f"Subtitles are disabled for this video, no transcript available."

def get_recommendations() -> dict:
    """
    Use Youtube API to get visual analysis of the video.
    """
    return {
        'prompt': """
Provide a detailed analysis focusing on:
1. Main topic and key points from the title and description
2. Expected visual elements and scenes
3. Overall message or purpose
4. Target audience
        """
    }

@tool
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
    transcript = get_transcript(video_id)
    recommendations = get_recommendations()

    try:
        result = f"# YouTube Video Data Obtained Successfully !\n\n"
        result += f"## Title\n'{text_details['title']}'\n\n"
        result += f"## Description\n'{text_details['description']}'\n\n"
        result += f"## Duration\n'{text_details['duration']} seconds'\n\n"
        result += f"## Transcript\n'{transcript}'\n\n"
        result += f"## Recommendations\n{recommendations['prompt']}\n\n"
        return result

    except Exception as e:
        return e
