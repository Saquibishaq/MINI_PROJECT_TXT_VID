import os
import requests
from gtts import gTTS
import moviepy.editor as mp
import torch
from transformers import pipeline
os.makedirs('static/videos', exist_ok=True)

# voice from text
def generate_voice(text, filename='voice.mp3'):
    """Generate voice for the given text using gTTS and save it as an MP3 file."""
    tts = gTTS(text, lang='en')
    tts.save(filename)

# videos from Pexels
def download_video(video_url, index):
    """Download the video from the given URL and save it as an MP4 file."""
    file_name = f'static/videos/video_{index}.mp4'
    response = requests.get(video_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    else:
        print(f"Error downloading video from {video_url}. Status code: {response.status_code}")
        return None   

# fetch videos from Pexels 
def fetch_videos(query, num_videos=5):  
    api_key = 'H1Z6bHv1l3etmP1J3wQl9Q1l3JNaL5PoypRPlQ9YNu9klqVOjGOVFWys'  
    url = f'https://api.pexels.com/videos/search?query={query}&per_page={num_videos}'
    headers = {'Authorization': api_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch videos. Status code: {response.status_code}")
        return []  

    data = response.json()

    if 'videos' not in data:
        print("Error: 'videos' key not found in the response.")
        return [] 
    
    video_links = [video['video_files'][0]['link'] for video in data['videos']]
    
    if not video_links:
        print("Warning: No video links found.")
    
    video_files = []
    for i, link in enumerate(video_links):
        print(f"Downloading video from link: {link}")
        video_file = download_video(link, i)
        if video_file:   
            video_files.append(video_file)
    
    return video_files

# create the final video from clips and audio
def create_final_video(video_files, voice_file, duration, output_file=None):
    """Concatenate the video clips and combine them with the generated voice."""
    
    if not video_files:
        print("Error: No video files to concatenate.")
        return None
    
    clips = []
    for video_file in video_files:
        try:
            clip = mp.VideoFileClip(video_file).subclip(0, min(30, mp.VideoFileClip(video_file).duration))
            clips.append(clip)
        except Exception as e:
            print(f"Error processing video file {video_file}: {e}")

    if not clips:
        print("Error: No valid video clips to concatenate.")
        return None
    
    final_video = mp.concatenate_videoclips(clips, method="compose")
    audio = mp.AudioFileClip(voice_file)

    final_duration = duration * 60   
    if audio.duration < final_duration:
        loops_needed = int(final_duration // audio.duration) + 1
        audio = mp.concatenate_audioclips([audio] * loops_needed)
        audio = audio.subclip(0, final_duration)
    if final_video.duration < final_duration:
        loops_needed = int(final_duration // final_video.duration) + 1
        final_video = mp.concatenate_videoclips([final_video] * loops_needed)
        final_video = final_video.subclip(0, final_duration)

    final_video.set_audio(audio)  

    if output_file is None:
        output_file = 'static/videos/final_video.mp4'   
    
    final_video.write_videofile(
        output_file, 
        codec='libx264', 
        audio_codec='aac', 
        threads=4, 
        preset='ultrafast',  
        fps=24,  
        bitrate='3000k',  
        ffmpeg_params=["-s", "640x360"]   
    )
    
    return output_file

def generate_text_from_prompt(prompt):
    """Generate a story based on the provided prompt using a text generation model."""
    device = 0 if torch.cuda.is_available() else -1
    generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B', device=device)
    generated = generator(prompt, max_length=500, do_sample=True)
    
    if not generated or len(generated) == 0:
        print("Error: No text generated.")
        return None  
    
    generated_text = generated[0]['generated_text'] if isinstance(generated, list) else ''
    return generated_text
def generate_video_story(prompt, duration):
    """Generate a video story based on the provided text and duration."""
    
    story = generate_text_from_prompt(prompt)
    if story is None:
        return None  
    print("Generated story:", story)
    generate_voice(story)  
    video_topic = story.split('.')[0]  
    video_files = fetch_videos(video_topic, num_videos=5)   
    return create_final_video(video_files, 'voice.mp3', duration) 
