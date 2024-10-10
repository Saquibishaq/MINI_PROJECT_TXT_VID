import asyncio
import aiohttp
from gtts import gTTS
import moviepy.editor as mp
import requests

def generate_voice(text, filename='voice.mp3'):
    tts = gTTS(text, lang='en')
    tts.save(filename)

async def download_video(session, video_url, index):
    async with session.get(video_url) as response:
        file_name = f'video_{index}.mp4'
        with open(file_name, 'wb') as f:
            f.write(await response.read())
        return file_name

async def fetch_videos(query, num_videos=5):
    api_key = 'H1Z6bHv1l3etmP1J3wQl9Q1l3JNaL5PoypRPlQ9YNu9klqVOjGOVFWys'
    url = f'https://api.pexels.com/videos/search?query={query}&per_page={num_videos}'
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    video_links = [video['video_files'][0]['link'] for video in data['videos']]
    
    async with aiohttp.ClientSession() as session:
        download_tasks = [download_video(session, link, i) for i, link in enumerate(video_links)]
        return await asyncio.gather(*download_tasks)

def create_final_video(video_files, voice_file, duration, output_file='final_video.mp4'):
    clips = [mp.VideoFileClip(video_file).subclip(0, 10) for video_file in video_files]
    final_video = mp.concatenate_videoclips(clips, method="compose")
    audio = mp.AudioFileClip(voice_file)
    final_duration = duration * 60
    audio = audio.subclip(0, min(final_duration, audio.duration))
    final_video = final_video.set_audio(audio)
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', threads=4, preset='fast')

async def main():
    story = input("Please enter your full text story: ")
    duration = int(input("Enter the duration in minutes: "))
    
    generate_voice(story)

    print("Choose a topic for the video:")
    topics = [
        "Fantasy", "Adventure", "Mystery", "Fairy Tale",
        "Horror", "Romance", "Historical Fiction", "Science Fiction",
        "Fable", "Mythology", "Comedy", "Drama",
        "Thriller", "Superhero", "Children's Story"
    ]
    for i, topic in enumerate(topics, start=1):
        print(f"{i}. {topic}")

    video_topic_index = int(input("Enter the number corresponding to the topic: ")) - 1
    selected_topic = topics[video_topic_index % len(topics)]
    
    video_files = await fetch_videos(selected_topic, num_videos=5)
    create_final_video(video_files, 'voice.mp3', duration)

main()
