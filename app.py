from flask import Flask, request, jsonify
from routes.video_routes import video_blueprint
import os  # Make sure to import os

app = Flask(__name__)
app.register_blueprint(video_blueprint)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
