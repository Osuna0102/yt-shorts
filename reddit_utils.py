import praw
import random
import re
from dotenv import load_dotenv
from pydub import AudioSegment
from text_to_speech_utils import text_to_speech
import os



# Load environment variables from .env file
load_dotenv()

# Reddit API credentials
reddit = praw.Reddit(
    client_id='KTzs73_IDYfsLsP5veOOlA',
    client_secret='yYE3cvJv2s0RljhKgeUYeFLG6Z-GIg',
    user_agent='yt-shorts-test'
)

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\S+', '', text)
    # Remove image paths or file paths
    text = re.sub(r'\S+\.(jpg|jpeg|png|gif|bmp|pdf|doc|docx|xls|xlsx|ppt|pptx)', '', text)
    # Remove any remaining unwanted characters or patterns
    text = re.sub(r'[^A-Za-z0-9\s.,!?\'"]+', '', text)
    return text

def fetch_random_reddit_story(subreddit, limit=50, min_comment_length=50, max_comment_length=300):
    submissions = list(reddit.subreddit(subreddit).top(limit=limit))
    random_submission = random.choice(submissions)
    
    # Filter comments based on length
    comments = [clean_text(comment.body) for comment in random_submission.comments if isinstance(comment, praw.models.Comment)]
    filtered_comments = [comment for comment in comments if min_comment_length <= len(comment) <= max_comment_length]
    
    story = {
        'title': clean_text(random_submission.title),
        'selftext': clean_text(random_submission.selftext),
        'comments': filtered_comments
    }
    return story

def combine_comments(story_text, comments, min_duration=40, max_duration=60):
    combined_text = story_text
    combined_audio = AudioSegment.silent(duration=0)
    
    # Generate audio for the story text
    story_audio_file = 'temp_story.mp3'
    text_to_speech(story_text, story_audio_file)
    story_audio = AudioSegment.from_mp3(story_audio_file)
    combined_audio += story_audio
    
    # Add comments until the combined duration is within the desired range
    for comment in comments:
        comment_audio_file = 'temp_comment.mp3'
        text_to_speech(comment, comment_audio_file)
        comment_audio = AudioSegment.from_mp3(comment_audio_file)
        
        if len(combined_audio) + len(comment_audio) > max_duration * 1000:
            break
        
        combined_text += " " + comment
        combined_audio += comment_audio
        
        if len(combined_audio) >= min_duration * 1000:
            break
    
    # Clean up temporary files
    os.remove(story_audio_file)
    os.remove(comment_audio_file)
    
    return combined_text, combined_audio