import os
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from moviepy.editor import *
from gtts import gTTS
from diffusers import StableDiffusionPipeline

# Load GPT-2 model and tokenizer for text generation
device = "cuda" if torch.cuda.is_available() else "cpu"
gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)

# Load Stable Diffusion for image generation
pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4").to(device)

# Ensure directories exist
os.makedirs('audio', exist_ok=True)
os.makedirs('assets', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Text-to-Story Generation using GPT-2
def generate_story(prompt, max_length=300):
    inputs = gpt2_tokenizer(prompt, return_tensors="pt").to(device)
    output = gpt2_model.generate(inputs['input_ids'], max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2)
    story = gpt2_tokenizer.decode(output[0], skip_special_tokens=True)
    return story

# Generate narration using local TTS (gTTS here for simplicity)
def generate_narration(text, filename="narration.mp3"):
    tts = gTTS(text)
    tts.save(os.path.join('audio', filename))

# Generate images using Stable Diffusion
def generate_images_from_story(story, num_images=5):
    sentences = story.split(". ")  # Split story into sentences for generating images
    images = []
    for i, sentence in enumerate(sentences[:num_images]):
        print(f"Generating image {i+1}/{num_images} for: {sentence}")
        image = pipe(sentence).images[0]
        image_path = f'assets/image_{i}.png'
        image.save(image_path)
        images.append(image_path)
    return images

# Assemble video with images and narration
def create_video(images, voice_file, output_file='output_video.mp4', min_duration=60):
    clips = []
    
    # Load the audio narration
    audio = AudioFileClip(voice_file)
    audio_duration = audio.duration

    # Final video duration calculation
    final_video_duration = max(audio_duration, min_duration)
    num_images = len(images)
    duration_per_image = final_video_duration / num_images if num_images > 0 else 1

    for img_path in images:
        img_clip = ImageClip(img_path).set_duration(duration_per_image).set_fps(24)
        clips.append(img_clip)

    # Concatenate images and set audio
    video = concatenate_videoclips(clips).set_audio(audio)

    # Write video to file
    video.write_videofile(output_file, codec='libx264', fps=24)

# Main function to drive the process
def main():
    prompt = input("Enter a prompt for the story: ")
    min_duration = int(input("Enter the minimum video duration (seconds): "))
    
    # Step 1: Generate a story from the prompt
    story = generate_story(prompt)
    print("Generated Story: ", story)
    
    # Step 2: Generate narration for the story
    generate_narration(story, filename="narration.mp3")
    
    # Step 3: Generate images using Stable Diffusion for the story
    images = generate_images_from_story(story, num_images=10)

    # Step 4: Create video from images and narration
    create_video(images, 'audio/narration.mp3', output_file="final_animation.mp4", min_duration=min_duration)
    print("Video created successfully!")

if __name__ == "__main__":
    main()
