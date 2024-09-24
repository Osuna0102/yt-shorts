import os
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from reddit_utils import fetch_random_reddit_story, combine_comments
from video_utils import create_video
from youtube_upload import upload_video_to_youtube, CREDENTIALS_FILES, TOKEN_FILES
from instagram_upload import upload_video_to_instagram  # Import the Instagram upload function

def main():
    load_dotenv()
    
    # List of popular subreddits for engaging stories
    subreddits = [
        'AskReddit',
        'AmItheAsshole',
        'TIFU',  # Today I F***ed Up
        'relationships',
        'relationship_advice',
        'confession',
        'LifeProTips',
        'ProRevenge',
        'MaliciousCompliance',
        'entitledparents',
        'ChoosingBeggars',
        'PettyRevenge'
    ]
    
    # Ask the user for the number of videos to generate and upload
    num_videos = int(input("How many videos do you want to generate and upload? "))
    
    # Create directories if they don't exist
    os.makedirs('audio', exist_ok=True)
    os.makedirs('clips', exist_ok=True)
    
    # List of background videos
    background_videos = ["background_videos/background1.mp4", "background_videos/background2.mp4"]  # Add paths to your background videos here
    
    for i in range(num_videos):
        # Select a random subreddit from the list
        subreddit = random.choice(subreddits)
        story = fetch_random_reddit_story(subreddit)
        
        # Combine story and comments to meet duration requirements
        combined_text, combined_audio = combine_comments(story['title'], story['comments'])
        
        # Save combined audio
        combined_audio_file = f'audio/combined_{i + 1}.mp3'
        combined_audio.export(combined_audio_file, format="mp3")
        
        # Create video file
        video_file = f'clips/story_{i + 1}.mp4'
        
        if not os.path.exists(video_file):
            create_video(combined_audio_file, video_file, background_videos)
        
        # Calculate the publish date and time (i days after the current time)
        publish_time = (datetime.now(timezone.utc) + timedelta(days=i + 1)).isoformat() + 'Z'  # 'Z' indicates UTC time
        
        # Use a round-robin approach to switch between credentials
        credentials_file = CREDENTIALS_FILES[i % len(CREDENTIALS_FILES)]
        token_file = TOKEN_FILES[i % len(TOKEN_FILES)]
        
        title = story['title']
        print(f"Original Title: {title}")  # Debugging statement
        
        description = combined_text
        tags = ['Reddit', 'Stories', 'YouTube Shorts']

        # Upload the video to Instagram Reels
        # upload_video_to_instagram(video_file, title, os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))

        # Upload the video to YouTube
        upload_video_to_youtube(video_file, title, description, tags, publish_time)
        
        # Clean up the audio file
        os.remove(combined_audio_file)
        
        # Clean up the video file only if it was generated in this run
        if os.path.exists(video_file):
            os.remove(video_file)

if __name__ == "__main__":
    main()