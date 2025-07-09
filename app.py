import os
import sys
from flask import Flask, render_template
from flask_cors import CORS
from vertexai.generative_models import GenerativeModel
import vertexai
from flask_dance.contrib.google import make_google_blueprint
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from api.v1.activities import activities_bp
from api.v1.users import bp as users_bp

app = Flask(
    __name__,
    static_folder='static/frontend/build/static',
    template_folder='static/frontend/build'
)

# .envからFLASK_SECRET_KEYを取得して設定
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_123")

# ProxyFixを適用（Cloud Run/リバースプロキシ対応）
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# FlaskのURL生成を本番用に固定（本番のみ有効）
if os.environ.get("FLASK_ENV") == "production":
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['SERVER_NAME'] = 'helth-report-129908471897.us-central1.run.app'

# Enable CORS
CORS(app, 
     resources={r"/*": {"origins": [
         "http://127.0.0.1:3000",
         "https://helth-report-129908471897.us-central1.run.app"
     ]}}, 
     supports_credentials=True, 
     methods=["GET", "POST", "DELETE", "PATCH", "OPTIONS"])

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "helth-report") # Get from env or use default
LOCATION = os.environ.get("GCP_LOCATION", "us-central1") # Get from env or use default
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Register Blueprints
app.register_blueprint(activities_bp)
app.register_blueprint(users_bp)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # APIリクエストはここで処理しない
    if path.startswith('api/') or path in ['login', 'logout', 'session', 'register']:
        return '', 404
    return render_template('index.html')

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used in production.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
