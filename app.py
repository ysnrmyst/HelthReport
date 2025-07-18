import os
import sys
from flask import Flask, render_template, send_from_directory
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
from api.v1.weekly_reflections import weekly_reflections_bp

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
    app.config['SERVER_NAME'] = 'health-report-465810-129908471897.us-central1.run.app'

# Cloud Run（本番環境）用セッションCookie設定
if os.environ.get("FLASK_ENV") == "production":
    app.config.update(
        SESSION_COOKIE_SECURE=True,      # HTTPSのみ
        SESSION_COOKIE_SAMESITE='None',  # クロスサイトでも送信
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_PATH='/'
    )
else:
    # 開発環境用設定
    app.config.update(
        SESSION_COOKIE_SECURE=False,     # HTTPでもOK
        SESSION_COOKIE_SAMESITE='Lax',   # 開発環境ではLax
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_PATH='/'
    )

# Enable CORS
CORS(app, 
     resources={r"/*": {"origins": [
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "https://health-report-465810-129908471897.us-central1.run.app",
         "https://health-report-465810-621003261884.us-central1.run.app"
     ]}}, 
     supports_credentials=True, 
     methods=["GET", "POST", "DELETE", "PATCH", "OPTIONS"])

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "health-report-465810") # Get from env or use default
LOCATION = os.environ.get("GCP_LOCATION", "us-central1") # Get from env or use default
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Register Blueprints
app.register_blueprint(activities_bp)
app.register_blueprint(users_bp, url_prefix='/api/v1')
app.register_blueprint(weekly_reflections_bp)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static/frontend/build', 'manifest.json')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # APIリクエストはここで処理しない
    if path.startswith('api/'):
        return '', 404
    # それ以外は全てindex.htmlを返す
    return render_template('index.html')

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used in production.
    print(app.url_map)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
