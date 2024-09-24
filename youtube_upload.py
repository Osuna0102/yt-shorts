import os
import re
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Define the credentials and token file paths
CREDENTIALS_FILES = 'credentials.json'
TOKEN_FILES = 'token.json'
COUNTER_FILE = 'counter.txt'

def authenticate_youtube():
    """Authenticate the user and return the YouTube service."""
    creds = None
    if os.path.exists(TOKEN_FILES):
        creds = Credentials.from_authorized_user_file(TOKEN_FILES, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILES, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILES, 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def read_counter():
    """Read the counter value from the file."""
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as file:
            return int(file.read().strip())
    return 0

def increment_counter():
    """Increment the counter value and save it to the file."""
    counter = read_counter() + 1
    with open(COUNTER_FILE, 'w') as file:
        file.write(str(counter))
    return counter

def sanitize_title(title):
    """Sanitize the video title to remove invalid characters and limit length."""
    counter = increment_counter()
    suffix = f"Reddit Stories [Shorts {counter}]"
    
    final_title = suffix.strip()  # Ensure no leading/trailing whitespace
    
    # Log the type, number of characters, and check for non-UTF-8 characters
    print(f"Sanitized Title: {final_title}")
    print(f"Type of Sanitized Title: {type(final_title)}")
    print(f"Number of Characters in Sanitized Title: {len(final_title)}")
    try:
        final_title.encode('utf-8')
        print("Sanitized Title is valid UTF-8")
    except UnicodeEncodeError:
        print("Sanitized Title contains non-UTF-8 characters")
    
    # Additional logging to check for hidden characters
    for i, char in enumerate(final_title):
        print(f"Character {i}: {char} (Unicode: {ord(char)})")
    
    return final_title

def upload_video_to_youtube(video_file, title, description, tags, publish_time):
    """Upload a video to YouTube."""
    youtube = authenticate_youtube()
    sanitized_title = sanitize_title(title)
    
    # Ensure the title or description includes the hashtag #Shorts and relevant tags
    hashtags = ['#Shorts', '#RedditStories', '#UpvotedReddit', '#ViralReddit', '#Storytime']
    for tag in hashtags:
        if tag not in sanitized_title:
            sanitized_title += f' {tag}'
        if tag not in description:
            description += f' {tag}'
    
    # Check if the sanitized title is not empty
    if not sanitized_title:
        raise ValueError("The sanitized video title is empty.")
    
    # Ensure publish_time is in the correct RFC 3339 format without 'Z' at the end
    if publish_time.endswith('Z'):
        publish_time = publish_time[:-1]
    
    request_body = {
        'snippet': {
            'title': sanitized_title,
            'description': description,
            'tags': tags + ['Reddit', 'Viral Stories', 'Storytime', 'Shorts', 'Reddit Comments'],
            'categoryId': '24',  # Entertainment category for better engagement
        },
        'status': {
            'privacyStatus': 'private',  # Start as 'private' until the scheduled publish time
            'publishAt': publish_time  # Schedule the video to be published at the specified time
        }
    }
    
    # Log the request body
    print(f"Request Body: {request_body}")
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print(f'Video uploaded: https://www.youtube.com/watch?v={response["id"]}')

# Example usage
if __name__ == "__main__":
    video_file = "path_to_your_video.mp4"
    title = "Your Video Title"
    description = "Your video description"
    tags = ["tag1", "tag2"]
    publish_time = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat()
    upload_video_to_youtube(video_file, title, description, tags, publish_time)