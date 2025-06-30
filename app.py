import os
import sys
from flask import Flask, render_template
from flask_cors import CORS
from vertexai.generative_models import GenerativeModel
import vertexai

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from api.v1.activities import activities_bp

app = Flask(
    __name__,
    static_folder='static/frontend/build/static',
    template_folder='static/frontend/build'
)

# Enable CORS
CORS(app)

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "helth-report") # Get from env or use default
LOCATION = os.environ.get("GCP_LOCATION", "us-central1") # Get from env or use default
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Register Blueprints
app.register_blueprint(activities_bp)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used in production.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
