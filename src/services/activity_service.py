from google.cloud import bigquery
from typing import List, Optional
import logging
from src.models.activity import ActivityCreate, ActivityUpdate, ActivityInDB

class ActivityService:
    def __init__(self, db_client: bigquery.Client, table_id: str):
        self.client = db_client
        self.table_id = table_id

    def create_activity(self, user_id: str, activity_data: ActivityCreate) -> Optional[ActivityInDB]:
        """新しい行動記録をBigQueryに挿入します。"""
        new_record = ActivityInDB(user_id=user_id, **activity_data.dict())
        
        rows_to_insert = [new_record.dict(by_alias=True)]
        errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
        
        if errors:
            logging.error(f"Failed to insert rows into BigQuery: {errors}")
            return None
        
        return new_record

    def get_activities_by_user(self, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[ActivityInDB]:
        """ユーザーIDに基づいて行動記録のリストを取得します。"""
        query = f""" 
            SELECT * 
            FROM `{self.table_id}`
            WHERE user_id = @user_id
        """
        params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]

        if start_date:
            query += " AND start_time >= @start_date"
            params.append(bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date))
        if end_date:
            query += " AND end_time <= @end_date"
            params.append(bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date))

        query += " ORDER BY start_time DESC"

        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        
        results = []
        for row in query_job:
            results.append(ActivityInDB(**row))
        
        return results

    def get_activity_by_id(self, activity_id: str, user_id: str) -> Optional[ActivityInDB]:
        """特定のIDとユーザーIDに基づいて行動記録を取得します。"""
        query = f"""
            SELECT * 
            FROM `{self.table_id}`
            WHERE id = @activity_id AND user_id = @user_id
            LIMIT 1
        """
        params = [
            bigquery.ScalarQueryParameter("activity_id", "STRING", activity_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]

        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        
        result = list(query_job.result())
        if result:
            return ActivityInDB(**result[0])
        return None

    def update_activity(self, activity_id: str, user_id: str, update_data: ActivityUpdate) -> Optional[ActivityInDB]:
        """既存の行動記録を更新します。"""
        updates = []
        params = [
            bigquery.ScalarQueryParameter("activity_id", "STRING", activity_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]

        # 更新対象のフィールドを動的に構築
        for field, value in update_data.dict(exclude_unset=True).items():
            if field == "start_time" or field == "end_time":
                updates.append(f"{field} = @{field}")
                params.append(bigquery.ScalarQueryParameter(field, "TIMESTAMP", value))
            elif field == "fatigue_level":
                updates.append(f"{field} = @{field}")
                params.append(bigquery.ScalarQueryParameter(field, "INT64", value))
            else:
                updates.append(f"{field} = @{field}")
                params.append(bigquery.ScalarQueryParameter(field, "STRING", value))
        
        if not updates:
            return self.get_activity_by_id(activity_id, user_id) # 更新データがない場合は現在のレコードを返す

        # updated_at を自動更新
        updates.append("updated_at = CURRENT_TIMESTAMP()");

        query = f"""
            UPDATE `{self.table_id}`
            SET {', '.join(updates)}
            WHERE id = @activity_id AND user_id = @user_id
        """
        
        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        query_job.result() # クエリの完了を待つ

        return self.get_activity_by_id(activity_id, user_id)

    def delete_activity(self, activity_id: str, user_id: str) -> bool:
        """特定のIDとユーザーIDに基づいて行動記録を削除します。"""
        query = f"""
            DELETE FROM `{self.table_id}`
            WHERE id = @activity_id AND user_id = @user_id
        """
        params = [
            bigquery.ScalarQueryParameter("activity_id", "STRING", activity_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]

        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        query_job.result() # クエリの完了を待つ

        # 削除が成功したかを確認するために、再度取得を試みる
        if self.get_activity_by_id(activity_id, user_id) is None:
            return True
        return False
