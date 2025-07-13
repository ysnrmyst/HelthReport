from flask import Blueprint, request, jsonify, session
from src.services.weekly_reflection_service import WeeklyReflectionService
from src.models.weekly_reflection import WeeklyReflectionCreate
from src.api.v1.users import login_required
from google.cloud import bigquery
from datetime import datetime, timedelta

weekly_reflections_bp = Blueprint('weekly_reflections', __name__, url_prefix='/api/v1/weekly-reflections')

# BigQueryクライアントとテーブルID（本番ではDIや設定ファイルで管理）
db_client = bigquery.Client()
table_id = 'health-report-465810.health-data.WeeklyReflections'  # 実際のBigQueryテーブルIDに修正
service = WeeklyReflectionService(db_client, table_id)

def get_week_dates(week_start_date):
    # 週の開始日から7日分の日付リストを返す
    start = datetime.strptime(week_start_date, '%Y-%m-%d')
    return [(start + timedelta(days=i)).date() for i in range(7)]

@weekly_reflections_bp.route('/ai-diagnosis', methods=['POST'])
def ai_diagnosis_route():
    print('=== [DEBUG] session:', dict(session))
    print('=== [DEBUG] session["user_id"]:', session.get('user_id'))
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "認証情報がありません"}), 401
    try:
        req_json = request.get_json()
        data = WeeklyReflectionCreate(**req_json)
        # AI診断コメント生成のみ（BigQuery保存は行わない）
        ai_comment = service.request_ai_diagnosis(req_json)
        return jsonify({"ai_comment": ai_comment}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@weekly_reflections_bp.route('', methods=['POST'])
def upsert_weekly_reflection_route():
    print('=== [DEBUG] session:', dict(session))
    print('=== [DEBUG] session["user_id"]:', session.get('user_id'))
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "認証情報がありません"}), 401
    try:
        req_json = request.get_json()
        print('=== [DEBUG] Request JSON:', req_json)
        data = WeeklyReflectionCreate(**req_json)
        print('=== [DEBUG] Parsed data:', data.dict())
        saved = service.upsert_weekly_reflection(user_id=user_id, data=data)
        return jsonify({"message": "保存しました", "data": saved.dict()}), 201
    except Exception as e:
        import traceback
        print(f"=== [ERROR] Exception in upsert_weekly_reflection_route: {str(e)} ===")
        print(f"=== [ERROR] Traceback: {traceback.format_exc()} ===")
        
        # BigQueryストリーミングバッファーエラーの検出
        error_message = str(e)
        if "streaming buffer" in error_message.lower():
            return jsonify({
                "error": "このデータは登録直後のため、2時間程度更新できない場合があります（BigQueryの仕様）。しばらくしてから再度お試しください。"
            }), 400
        
        return jsonify({"error": str(e)}), 400

@weekly_reflections_bp.route('', methods=['GET'])
def get_weekly_reflections_route():
    print('=== [DEBUG] Weekly Reflections API called ===')
    print('=== [DEBUG] session:', dict(session))
    print('=== [DEBUG] session["user_id"]:', session.get('user_id'))
    print('=== [DEBUG] request.headers:', dict(request.headers))
    print('=== [DEBUG] request.args:', dict(request.args))
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "認証情報がありません"}), 401
    try:
        # デバッグ用：現在のユーザーIDをログ出力
        print(f"=== [DEBUG] Current user_id: {user_id} ===")
        
        # クエリパラメータで週の開始日を指定可能（例: ?week_start_date=2024-07-01）
        week_start_date = request.args.get('week_start_date')
        print(f"=== [DEBUG] week_start_date: {week_start_date} ===")
        reflections = service.get_weekly_reflections(user_id=user_id, week_start_date=week_start_date)
        return jsonify([r.dict() for r in reflections]), 200
    except Exception as e:
        print(f"=== [ERROR] Exception in weekly reflections API: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400 

@weekly_reflections_bp.route('/weekly-load-summary', methods=['GET'])
def get_weekly_load_summary():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "認証情報がありません"}), 401
    week_start_date = request.args.get('week_start_date')
    if not week_start_date:
        return jsonify({"error": "week_start_date is required"}), 400

    # BigQueryクエリで週次合計と日別サマリーを取得
    db_client = bigquery.Client()
    activities_table_id = 'health-report-465810.health-data.activities'
    week_dates = get_week_dates(week_start_date)
    week_end_date = week_dates[-1]

    # 日別サマリー
    query = f"""
    SELECT DATE(start_time) as date,
           SUM(TIMESTAMP_DIFF(end_time, start_time, MINUTE)) as activity_minutes,
           SUM(fatigue_level * (TIMESTAMP_DIFF(end_time, start_time, MINUTE) / 60.0)) as load_points
    FROM `{activities_table_id}`
    WHERE user_id = @user_id
      AND DATE(start_time) BETWEEN @week_start_date AND @week_end_date
      AND category_id IN ('business', 'study', 'private')
    GROUP BY date
    ORDER BY date
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("week_start_date", "DATE", week_start_date),
            bigquery.ScalarQueryParameter("week_end_date", "DATE", str(week_end_date)),
        ]
    )
    results = list(db_client.query(query, job_config=job_config).result())
    daily = []
    total_load_points = 0
    for row in results:
        daily.append({
            "date": str(row["date"]),
            "activity_minutes": int(row["activity_minutes"] or 0),
            "load_points": float(row["load_points"] or 0)
        })
        total_load_points += float(row["load_points"] or 0)
    return jsonify({
        "total_load_points": total_load_points,
        "daily": daily
    }) 