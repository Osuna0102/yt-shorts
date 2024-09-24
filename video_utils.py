from PIL import Image
import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip
import os
import random
import logging
import shutil
from google.cloud import speech
from dotenv import load_dotenv
from image_utils import create_text_image

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def custom_resize(clip, newsize):
    def resize_image(image):
        pil_image = Image.fromarray(image)
        resized_pil_image = pil_image.resize(newsize[::-1], Image.LANCZOS)
        return np.array(resized_pil_image)
    return clip.fl_image(resize_image)

def transcribe_audio(audio_file):
    client = speech.SpeechClient(client_options={"api_key": GOOGLE_API_KEY})
    
    with open(audio_file, "rb") as audio:
        content = audio.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    response = client.recognize(config=config, audio=audio)
    return response

def create_subtitle_clips_from_transcription(transcription, temp_folder="temp"):
    subtitle_clips = []
    os.makedirs(temp_folder, exist_ok=True)

    phrases = []
    current_phrase = ""
    current_start_time = None
    gap_duration = 0.15  # 200 milliseconds gap between phrases

    for result in transcription.results:
        for alternative in result.alternatives:
            for word_info in alternative.words:
                word = word_info.word
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()

                if current_start_time is None:
                    current_start_time = start_time

                if len(current_phrase) + len(word) + 1 > 60:  # Adjust the length as needed
                    phrases.append((current_phrase, current_start_time, end_time))
                    current_phrase = word
                    current_start_time = end_time + gap_duration
                else:
                    if current_phrase:
                        current_phrase += " "
                    current_phrase += word

            if current_phrase:
                phrases.append((current_phrase, current_start_time, end_time))
                current_phrase = ""
                current_start_time = None

    for i, (text, start_time, end_time) in enumerate(phrases):
        duration = end_time - start_time
        subtitle_image_file = os.path.join(temp_folder, f"subtitle_{i}.png")
        create_text_image(text, subtitle_image_file, width=1080, height=600, font_size=70)  # Adjust height for subtitles
        subtitle_clip = ImageClip(subtitle_image_file).set_duration(duration).set_start(start_time).set_position("center").set_opacity(0.8)
        subtitle_clips.append(subtitle_clip)

    return subtitle_clips

def create_video(combined_audio_file, output_file, background_videos):
    logging.basicConfig(level=logging.DEBUG)
    try:
        temp_folder = "temp"
        os.makedirs(temp_folder, exist_ok=True)
        
        # Create audio clip
        combined_audio_clip = AudioFileClip(combined_audio_file)
        combined_duration = combined_audio_clip.duration

        # Select a random background video
        background_video = random.choice(background_videos)
        background_clip = VideoFileClip(background_video)

        # Pick a random start time for the background video
        max_start_time = background_clip.duration - combined_duration
        start_time = random.uniform(0, max_start_time)
        background_clip = background_clip.subclip(start_time, start_time + combined_duration)

        # Resize background clip to 1080x1920 (9:16 aspect ratio)
        background_clip = custom_resize(background_clip, (1080, 1920))

        # Transcribe audio to get subtitles
        transcription = transcribe_audio(combined_audio_file)

        # Create subtitle clips from transcription
        subtitle_clips = create_subtitle_clips_from_transcription(transcription, temp_folder)

        # Composite the text image over the background video
        final_video = CompositeVideoClip([background_clip.set_duration(combined_duration).set_audio(combined_audio_clip)] + subtitle_clips)

        # Ensure the final video is saved with the correct aspect ratio
        final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac', preset='medium', ffmpeg_params=['-vf', 'scale=1080:1920'])

        shutil.rmtree(temp_folder)  # Clean up temporary folder
    except Exception as e:
        logging.error(f"Error creating video: {e}", exc_info=True)