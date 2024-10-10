from flask import Flask, request, jsonify
from routes.video_routes import video_blueprint

app = Flask(__name__)
app.register_blueprint(video_blueprint)

if __name__ == "__main__":
    app.run(debug=True)

