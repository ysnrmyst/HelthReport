import os
import sys
from flask import Flask, render_template
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

# Initialize Vertex AI
# TODO: Replace with your actual project ID and location
PROJECT_ID = "helth-report"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Register Blueprints
app.register_blueprint(activities_bp)

@app.route('/')
def index():
    # Serve the React app's index.html
    return render_template('index.html')

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used in production.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
