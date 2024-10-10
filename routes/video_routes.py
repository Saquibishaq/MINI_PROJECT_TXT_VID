from flask import Blueprint, request, jsonify
from services.video_service import generate_video_story

video_blueprint = Blueprint('video', __name__)

@video_blueprint.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.json
    text_prompt = data.get('prompt')

    if not text_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    video_path = generate_video_story(text_prompt)
    return jsonify({"video_path": video_path}), 200
