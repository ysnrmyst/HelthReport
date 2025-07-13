from flask import Blueprint, request, jsonify, session
from google.cloud import bigquery
from src.services.user_service import UserService
import bcrypt
import uuid
from datetime import datetime
from functools import wraps

bp = Blueprint('users', __name__)

# UserServiceインスタンス生成
bq_client = bigquery.Client()
table_id = 'health-report-465810.health-data.users'
user_service = UserService(bq_client, table_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'login required'}), 401
        return f(user_id, *args, **kwargs)
    return decorated_function

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    # 既存ユーザチェック
    if user_service.get_user_by_username(username):
        return jsonify({'error': 'username already exists'}), 400

    # パスワードハッシュ化
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    user = {
        'id': user_id,
        'username': username,
        'password_hash': password_hash,
        'created_at': now,
        'updated_at': now
    }
    user_service.create_user(user)
    return jsonify({'message': 'user created', 'user_id': user_id}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    user = user_service.get_user_by_username(username)
    if not user:
        return jsonify({'error': 'invalid username or password'}), 401

    # パスワード照合
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'invalid username or password'}), 401

    # セッションにuser_idを保存
    session['user_id'] = user['id']
    return jsonify({'message': 'login successful', 'user_id': user['id'], 'username': user['username']}), 200

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'logout successful'}), 200

@bp.route('/session', methods=['GET'])
def session_status():
    user_id = session.get('user_id')
    if user_id:
        # ユーザー名も返す
        user = user_service.get_user_by_username_or_id(user_id)
        username = user['username'] if user else None
        return jsonify({'logged_in': True, 'user_id': user_id, 'username': username}), 200
    else:
        return jsonify({'logged_in': False}), 200 