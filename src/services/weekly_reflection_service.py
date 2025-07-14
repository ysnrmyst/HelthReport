from google.cloud import bigquery
from src.models.weekly_reflection import WeeklyReflectionCreate, WeeklyReflectionInDB
from typing import Optional
from datetime import datetime, timedelta, date
import uuid
import json
from vertexai.generative_models import GenerativeModel
import vertexai

class WeeklyReflectionService:
    def __init__(self, db_client: bigquery.Client, table_id: str):
        self.client = db_client
        self.table_id = table_id

    def calculate_weekly_load_points(self, user_id: str, week_start_date: date) -> int:
        """
        指定された週の日々の負荷ポイントを合計する
        fatigue_level * 作業時間（分）を負荷ポイントとして計算
        """
        # 週の開始日から7日間の期間を計算
        week_end_date = week_start_date + timedelta(days=6)
        
        # Activitiesテーブルから該当週の負荷ポイントを取得
        # fatigue_level * 作業時間（分）を負荷ポイントとして計算
        activities_table_id = 'health-report-465810.health_data.activities'
        
        query = f"""
        SELECT COALESCE(SUM(
          fatigue_level * 
          (TIMESTAMP_DIFF(end_time, start_time, MINUTE) / 60.0)
        ), 0) as total_load_points
        FROM `{activities_table_id}`
        WHERE user_id = @user_id 
        AND DATE(start_time) BETWEEN @week_start_date AND @week_end_date
        AND category_id IN ('business', 'study', 'private')
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("week_start_date", "DATE", str(week_start_date)),
                bigquery.ScalarQueryParameter("week_end_date", "DATE", str(week_end_date))
            ]
        )
        
        results = list(self.client.query(query, job_config=job_config).result())
        return results[0]["total_load_points"] if results else 0

    def create_weekly_reflection(self, user_id: str, data: WeeklyReflectionCreate) -> Optional[WeeklyReflectionInDB]:
        print(f"=== [DEBUG] create_weekly_reflection called with user_id: {user_id} ===")
        now = datetime.utcnow()
        
        # 週次負荷ポイント合計を計算
        weekly_total_load_points = self.calculate_weekly_load_points(user_id, data.week_start_date)
        
        questions_json = json.dumps([q.dict() for q in data.questions]) if data.questions else None
        row = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "week_start_date": str(data.week_start_date),
            "reflection_notes": data.reflection_notes,
            "title": data.title,
            "questions": questions_json,
            "anxieties": data.anxieties,
            "good_things": data.good_things,
            "ai_diagnosis_result": data.ai_diagnosis_result,
            "weekly_total_load_points": weekly_total_load_points,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        print(f"=== [DEBUG] Inserting row: {row} ===")
        errors = self.client.insert_rows_json(self.table_id, [row])
        if errors:
            print(f"=== [ERROR] BigQuery insert errors: {errors} ===")
            raise Exception(f"BigQuery insert error: {errors}")
        print("=== [DEBUG] Insert successful ===")
        # questionsをリストに戻してからPydanticモデルに渡す
        row["questions"] = json.loads(row["questions"]) if row["questions"] else []
        return WeeklyReflectionInDB(**row)

    def request_ai_diagnosis(self, data: dict) -> str:
        """
        Vertex AI Geminiで週次振り返りAI診断コメントを生成する。
        data: {
            "title": str,
            "questions": [{"text": str, "score": int}, ...],
            "anxieties": str,
            "good_things": str
        }
        """
        # プロンプト生成（ペルソナ強化＆指摘＋ポジティブ締め）
        prompt = f"""
あなたは優しいカウンセラーです。以下の週次振り返り内容をもとに、ユーザーが前向きになれるような温かいコメントを日本語で200文字程度で作成してください。
特に、スコアが低い設問や「不安なこと」には的確に触れつつ、最後は必ずポジティブな励ましや安心できる言葉で締めくくってください。

【タイトル】
{data.get('title', '')}

【設問とスコア】
"""
        for q in data.get('questions', []):
            prompt += f"・{q.get('text', '')}：{q.get('score', '')}点\n"
        prompt += f"\n【不安なこと】\n{data.get('anxieties', '')}\n"
        prompt += f"\n【良かったこと】\n{data.get('good_things', '')}\n"
        prompt += "\n---\n\nコメント："

        # Geminiモデル呼び出し
        try:
            model = GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"AI診断コメント生成中にエラーが発生しました: {e}"

    def get_weekly_reflections(self, user_id: str, week_start_date: Optional[str] = None):
        # デバッグ用：ユーザーIDをログ出力
        print(f"=== [DEBUG] Service user_id: {user_id} ===")
        
        # BigQueryからユーザーの週次振り返りを取得
        query = f"""
        SELECT * FROM `{self.table_id}`
        WHERE user_id = @user_id
        """
        print(f"=== [DEBUG] Query: {query} ===")
        print(f"=== [DEBUG] user_id parameter: {user_id} ===")
        query_parameters = [
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
        
        if week_start_date:
            query += " AND week_start_date = @week_start_date"
            query_parameters.append(
                bigquery.ScalarQueryParameter("week_start_date", "DATE", week_start_date)
            )
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query += " ORDER BY week_start_date DESC"
        results = self.client.query(query, job_config=job_config).result()
        reflections = []
        for row in results:
            # questionsはJSON型なのでlistに変換（型チェック）
            if row["questions"]:
                if isinstance(row["questions"], str):
                    questions = json.loads(row["questions"])
                else:
                    questions = row["questions"]
            else:
                questions = []
            reflection = WeeklyReflectionInDB(
                id=row["id"],
                user_id=row["user_id"],
                week_start_date=row["week_start_date"],
                most_frequent_category_id=row.get("most_frequent_category_id"),
                reflection_notes=row.get("reflection_notes"),
                ai_diagnosis_result=row.get("ai_diagnosis_result"),
                title=row.get("title"),
                questions=questions,
                anxieties=row.get("anxieties"),
                good_things=row.get("good_things"),
                weekly_total_load_points=row.get("weekly_total_load_points"),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            reflections.append(reflection)
        return reflections

    def upsert_weekly_reflection(self, user_id: str, data: WeeklyReflectionCreate) -> Optional[WeeklyReflectionInDB]:
        print(f"=== [DEBUG] upsert_weekly_reflection called with user_id: {user_id}, week_start_date: {data.week_start_date} ===")
        
        # 既存レコードの有無を確認
        query = f"""
        SELECT id FROM `{self.table_id}`
        WHERE user_id = @user_id AND week_start_date = @week_start_date
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("week_start_date", "DATE", str(data.week_start_date))
            ]
        )
        results = list(self.client.query(query, job_config=job_config).result())
        print(f"=== [DEBUG] Existing records found: {len(results)} ===")
        
        # 週次負荷ポイント合計を計算
        weekly_total_load_points = self.calculate_weekly_load_points(user_id, data.week_start_date)
        print(f"=== [DEBUG] Weekly total load points: {weekly_total_load_points} ===")
        
        if results:
            # UPDATE
            row_id = results[0]["id"]
            print(f"=== [DEBUG] Updating existing record with id: {row_id} ===")
            update_query = f"""
            UPDATE `{self.table_id}`
            SET
              reflection_notes = @reflection_notes,
              title = @title,
              questions = @questions,
              anxieties = @anxieties,
              good_things = @good_things,
              ai_diagnosis_result = @ai_diagnosis_result,
              weekly_total_load_points = @weekly_total_load_points,
              updated_at = CURRENT_TIMESTAMP()
            WHERE id = @id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("reflection_notes", "STRING", data.reflection_notes),
                    bigquery.ScalarQueryParameter("title", "STRING", data.title),
                    bigquery.ScalarQueryParameter("questions", "JSON", json.dumps([q.dict() for q in data.questions]) if data.questions else None),
                    bigquery.ScalarQueryParameter("anxieties", "STRING", data.anxieties),
                    bigquery.ScalarQueryParameter("good_things", "STRING", data.good_things),
                    bigquery.ScalarQueryParameter("ai_diagnosis_result", "STRING", data.ai_diagnosis_result),
                    bigquery.ScalarQueryParameter("weekly_total_load_points", "INT64", weekly_total_load_points),
                    bigquery.ScalarQueryParameter("id", "STRING", row_id)
                ]
            )
            try:
                self.client.query(update_query, job_config=job_config).result()
                print("=== [DEBUG] Update successful ===")
            except Exception as e:
                print(f"=== [ERROR] Update failed: {str(e)} ===")
                raise e
            # 返却用に再取得
            return self.get_weekly_reflections(user_id, str(data.week_start_date))[0]
        else:
            # INSERT（今まで通り）
            print("=== [DEBUG] Creating new record ===")
            try:
                return self.create_weekly_reflection(user_id, data)
            except Exception as e:
                print(f"=== [ERROR] Create failed: {str(e)} ===")
                raise e 