from openai import OpenAI
import os, sys, json
import wikipedia
import wikipediaapi
from gtts import gTTS
import gtts.lang
from google.cloud import texttospeech
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, TextClip

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key here"

def create_video_from_audio_and_images(audio_path, images_with_timestamps, output_path):
    """
    Create a video from an audio file and a sequence of images with timestamps.

    :param audio_path: Path to the input MP3 file.
    :param images_with_timestamps: List of tuples (image_path, start_time, duration).
                                   - image_path: Path to the image file.
                                   - start_time: Start time of the image in seconds.
                                   - duration: Duration of the image display in seconds.
    :param output_path: Path to save the output video file.
    """
    try:
        # Load the audio file
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        
        # Create image clips
        image_clips = []
        for img_path, start_time, duration in images_with_timestamps:
            # Create an ImageClip with specified duration
            image_clip = (
                ImageClip(img_path)
                .set_start(start_time)
                .set_duration(duration)
                .set_position("center")
                .resize(height=720)  # Resize to fit the video (optional)
            )
            image_clips.append(image_clip)
        
        # Concatenate all image clips
        final_clip = concatenate_videoclips(image_clips, method="compose")

        # Set the audio file to the video
        final_clip = final_clip.set_audio(audio)

        # Ensure the video duration matches the audio
        final_clip = final_clip.set_duration(total_duration)

        # Export the video
        final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        print(f"Video created successfully: {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def call_llm(content):
    client = OpenAI(
        api_key="key here"
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer", 
                "content": """You are a Youtube channel making short-form interesting trivia content 
                speaking in modern conversational mix of Tagalog-English "Taglish" language. 
                Format the answers into multiple contents where each content takes around 1 minute each to read. 
                Only include the most interesting facts.
                Make the title catchy for Tiktok/Youtube. Separate each answer like a python Dictionary with title and content as keys.
                Output it directly as a JSON file, so I can parse it directly. Don't add any other words. I want to see [{ immediately.
                """},
            {
                "role": "user",
                "content": content
            }
        ]
    )
    return completion.choices[0].message

def fetch_wikipedia_content():
    """
    Fetch and parse the Wikipedia page content for a given subject.
    """
    subject = input("Enter a topic to search on Wikipedia: ")
    try:
        # Initialize the Wikipedia API
        wiki_wiki = wikipediaapi.Wikipedia('video-gener8 1.0','en')
        
        # Search for the subject
        print(f"Searching for '{subject}' on Wikipedia...")
        wikipedia.set_lang('en')
        search_results = wikipedia.search(subject, results=5)
        
        if not search_results:
            print("No results found. Please try another subject.")
            return None
        
        # print(f"Found related topics: {', '.join(search_results)}")
        page_name = search_results[0]  # Select the first result
        
        # print(f"Fetching the page: '{page_name}'...")
        page = wiki_wiki.page(page_name)
        
        if not page.exists():
            print(f"The page '{page_name}' does not exist.")
            return None
        
        # Parse content
        # print(f"Page Title: {page.title}")
        # print(f"Page URL: {page.fullurl}")
        # print("Fetching content...")
        
        return {
            "title": page.title,
            "url": page.fullurl,
            "summary": page.summary,
            "full_content": page.text
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def generate_speech_tts(text, output_file="output.mp3"):
    tts = gTTS(text=text, lang="tl")
    tts.save(output_file)
    print(f"Audio saved as {output_file}")

def generate_speech(text, output_file="output.mp3"):
    client = texttospeech.TextToSpeechClient()

    # Configure text input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Select language code and voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="fil-PH",  # Filipino language code
        name="fil-ph-Neural2-D",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    # Configure audio settings
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform TTS
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save the output
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    print(f"Audio content written to {output_file}")

# generate_speech("Kumusta! Paano kita matutulungan ngayon?")

if __name__ == "__main__":
    # # Define input files
    # audio_path = "output2.mp3"
    # images_with_timestamps = [
    #     ("image1.jpg", 0, 5),    # Display image1.jpg from 0s to 5s
    #     ("image2.jpg", 5, 5),    # Display image2.jpg from 5s to 10s
    #     ("image3.jpg", 10, 5),   # Display image3.jpg from 10s to 15s
    # ]
    # output_path = "output_video.mp4"

    # # Create the video
    # create_video_from_audio_and_images(audio_path, images_with_timestamps, output_path)
    # # print(gtts.lang.tts_langs())
    
    # # Input subject to search
    
    result = fetch_wikipedia_content()
    if not result:
        sys.exit(1)

    input("Press Enter to continue to LLM call...")
        # print("\n--- Page Summary ---")
        # print(result["summary"])
        # print("\n--- Full Content ---")
        # print(result["full_content"][:1000])  # Pr
    llm_message = call_llm(result["full_content"][:2000])
    print(llm_message.content)
    answers = json.loads(llm_message.content)
    print(answers)
        # generate_speech_tts(llm_message.content, output_file="output2.mp3")
    generate_speech(llm_message.content)
        