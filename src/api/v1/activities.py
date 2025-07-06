from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from src.models.activity import ActivityCreate, ActivityUpdate
from src.services.activity_service import ActivityService
from src.core.db import get_db_client

# これは一時的なものです。後で依存性注入のパターンにリファクタリングします。
# TODO: テーブルIDを環境変数から取得するように修正
TABLE_ID = "helth-report.health_data.activities"
db_client = get_db_client()
activity_service = ActivityService(db_client=db_client, table_id=TABLE_ID)

activities_bp = Blueprint('activities', __name__, url_prefix='/api/v1/activities')

@activities_bp.route('', methods=['POST'])
def create_activity_route():
    # TODO: 認証デコレータを追加 (user_idをそこから取得)
    user_id = "test-user" # 仮のユーザーID

    print("=== POST /api/v1/activities 受信 ===")
    print(request.json)
    
    try:
        activity_data = ActivityCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    new_activity = activity_service.create_activity(user_id=user_id, activity_data=activity_data)

    if not new_activity:
        return jsonify({"error": "Failed to create activity"}), 500

    return jsonify(new_activity.dict()), 201

@activities_bp.route('', methods=['GET'])
def get_activities_route():
    # TODO: 認証デコレータを追加 (user_idをそこから取得)
    user_id = "test-user" # 仮のユーザーID

    # TODO: クエリパラメータから日付範囲を取得
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    activities = activity_service.get_activities_by_user(
        user_id=user_id, 
        start_date=start_date, 
        end_date=end_date
    )
    
    return jsonify([activity.dict() for activity in activities]), 200

@activities_bp.route('/<activity_id>', methods=['GET'])
def get_activity_route(activity_id):
    # TODO: 認証デコレータを追加 (user_idをそこから取得)
    user_id = "test-user" # 仮のユーザーID

    activity = activity_service.get_activity_by_id(activity_id=activity_id, user_id=user_id)

    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    return jsonify(activity.dict()), 200

@activities_bp.route('/<activity_id>', methods=['PATCH'])
def update_activity_route(activity_id):
    # TODO: 認証デコレータを追加 (user_idをそこから取得)
    user_id = "test-user" # 仮のユーザーID

    try:
        update_data = ActivityUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    updated_activity = activity_service.update_activity(activity_id=activity_id, user_id=user_id, update_data=update_data)

    if not updated_activity:
        return jsonify({"error": "Activity not found or failed to update"}), 404

    return jsonify(updated_activity.dict()), 200

@activities_bp.route('/<activity_id>', methods=['DELETE'])
def delete_activity_route(activity_id):
    # TODO: 認証デコレータを追加 (user_idをそこから取得)
    user_id = "test-user" # 仮のユーザーID

    try:
        deleted = activity_service.delete_activity(activity_id=activity_id, user_id=user_id)
    except Exception as e:
        # BigQueryストリーミングバッファエラーを検出
        if 'would affect rows in the streaming buffer' in str(e):
            return jsonify({
                "error": "このデータは登録直後のため、2時間程度削除できない場合があります（BigQueryの仕様）。しばらくしてから再度お試しください。"
            }), 400
        # その他のエラーは500で返す
        return jsonify({"error": str(e)}), 500

    if not deleted:
        return jsonify({"error": "Activity not found or failed to delete"}), 404

    return '', 204
