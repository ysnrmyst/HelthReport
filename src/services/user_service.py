from google.cloud import bigquery
from typing import Optional
import logging
from src.models.user import UserCreate, UserInDB

class UserService:
    def __init__(self, db_client: bigquery.Client, table_id: str):
        self.client = db_client
        self.table_id = table_id

    def upsert_user(self, user_data: UserCreate) -> Optional[UserInDB]:
        """ユーザー情報をBigQueryにUPSERT（MERGE）します。"""
        try:
            # MERGEクエリでUPSERT処理を実行
            query = f"""
                MERGE `{self.table_id}` AS target
                USING (
                    SELECT 
                        @google_id as google_id,
                        @email as email,
                        @display_name as display_name,
                        @profile_picture_url as profile_picture_url,
                        CURRENT_TIMESTAMP() as updated_at
                ) AS source
                ON target.google_id = source.google_id
                WHEN MATCHED THEN
                    UPDATE SET
                        email = source.email,
                        display_name = source.display_name,
                        profile_picture_url = source.profile_picture_url,
                        updated_at = source.updated_at
                WHEN NOT MATCHED THEN
                    INSERT (
                        id, google_id, email, display_name, profile_picture_url, 
                        created_at, updated_at
                    )
                    VALUES (
                        GENERATE_UUID(), source.google_id, source.email, 
                        source.display_name, source.profile_picture_url,
                        CURRENT_TIMESTAMP(), source.updated_at
                    )
            """
            
            params = [
                bigquery.ScalarQueryParameter("google_id", "STRING", user_data.google_id),
                bigquery.ScalarQueryParameter("email", "STRING", user_data.email),
                bigquery.ScalarQueryParameter("display_name", "STRING", user_data.display_name),
                bigquery.ScalarQueryParameter("profile_picture_url", "STRING", user_data.profile_picture_url)
            ]

            query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
            query_job.result()  # クエリの完了を待つ

            # UPSERT後のユーザー情報を取得
            return self.get_user_by_google_id(user_data.google_id)

        except Exception as e:
            logging.error(f"Failed to upsert user into BigQuery: {e}")
            return None

    def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        """Google IDに基づいてユーザー情報を取得します。"""
        query = f"""
            SELECT * 
            FROM `{self.table_id}`
            WHERE google_id = @google_id
            LIMIT 1
        """
        params = [bigquery.ScalarQueryParameter("google_id", "STRING", google_id)]

        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        
        result = list(query_job.result())
        if result:
            return UserInDB(**result[0])
        return None

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """メールアドレスに基づいてユーザー情報を取得します。"""
        query = f"""
            SELECT * 
            FROM `{self.table_id}`
            WHERE email = @email
            LIMIT 1
        """
        params = [bigquery.ScalarQueryParameter("email", "STRING", email)]

        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        
        result = list(query_job.result())
        if result:
            return UserInDB(**result[0])
        return None

    def get_user_by_username(self, username: str):
        """
        usernameでユーザー情報を取得
        """
        query = f"""
            SELECT * FROM `{self.table_id}`
            WHERE username = @username
            LIMIT 1
        """
        params = [bigquery.ScalarQueryParameter("username", "STRING", username)]
        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        result = list(query_job.result())
        if result:
            return result[0]
        return None

    def get_user_by_username_or_id(self, value: str):
        """
        usernameまたはuser_idでユーザー情報を取得
        """
        query = f"""
            SELECT * FROM `{self.table_id}`
            WHERE username = @value OR id = @value
            LIMIT 1
        """
        params = [bigquery.ScalarQueryParameter("value", "STRING", value)]
        query_job = self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params))
        result = list(query_job.result())
        if result:
            return result[0]
        return None

    def create_user(self, user: dict):
        """
        新規ユーザーをBigQueryにINSERT
        """
        errors = self.client.insert_rows_json(self.table_id, [user])
        if errors:
            raise Exception(f"BigQuery insert error: {errors}")
        return True 