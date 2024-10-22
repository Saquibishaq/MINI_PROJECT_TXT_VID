import os
from flask import Blueprint, request, jsonify, url_for
from services.video_service import generate_video_story

video_bp = Blueprint('video', __name__)

@video_bp.route('/generate', methods=['POST'])
def generate_video():
    data = request.json
    prompt = data.get('prompt')
    duration = data.get('duration', 1)  # Default duration to 1 minute if not provided
    
    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400
    
    # Generate video
    output_video_path = generate_video_story(prompt, duration)
    
    if output_video_path and os.path.exists(output_video_path):
        # Generate URL to serve the video
        video_url = url_for('static', filename=f'videos/{os.path.basename(output_video_path)}', _external=True)
        return jsonify({'video_url': video_url}), 200
    else:
        return jsonify({'error': 'Video generation failed.'}), 500

