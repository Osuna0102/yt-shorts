import os
from google.cloud import texttospeech
from pydub import AudioSegment
from split_text_utils import split_text
import logging

def text_to_speech(text, filename):
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

    logging.debug(f"Text to synthesize: {text}")

    # Create a client with the API key
    client = texttospeech.TextToSpeechClient(
        client_options={"api_key": api_key}
    )

    chunks = split_text(text)
    audio_segments = []

    for i, chunk in enumerate(chunks):
        input_text = texttospeech.SynthesisInput(text=chunk)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-B"  # Specify the male voice
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )
        except Exception as e:
            logging.error(f"Error synthesizing speech: {e}")
            continue

        temp_filename = f"{filename}_part_{i}.mp3"
        with open(temp_filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Audio content written to file {temp_filename}')
        audio_segments.append(AudioSegment.from_mp3(temp_filename))

    # Concatenate all audio segments
    if audio_segments:
        combined_audio = sum(audio_segments)
        combined_audio.export(filename, format="mp3")
        print(f'Combined audio content written to file {filename}')

    # Clean up temporary files
    for i in range(len(chunks)):
        temp_filename = f"{filename}_part_{i}.mp3"
        if os.path.exists(temp_filename):
            os.remove(temp_filename)