import os
import os
from google.cloud import bigquery

def get_db_client() -> bigquery.Client:
    """BigQueryクライアントを取得します。"""
    # TODO: プロジェクトIDや認証情報を環境変数から読み込む
    # TODO: プロジェクトIDや認証情報を環境変数から読み込む
    # Cloud Run環境では、サービスアカウントが自動的に認証情報を提供するため、
    # 明示的な認証情報の設定は不要な場合が多いですが、プロジェクトIDは明示的に指定します。
    project_id = os.environ.get("GCP_PROJECT_ID", "helth-report")
    return bigquery.Client(project=project_id)
