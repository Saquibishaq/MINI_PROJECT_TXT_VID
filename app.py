from flask import Flask
from routes.video_routes import video_bp

app = Flask(__name__)
app.register_blueprint(video_bp)

# Ensure videos are saved in a 'static/videos' folder and Flask can serve them
app.config['UPLOAD_FOLDER'] = 'static/videos'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
