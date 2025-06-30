from google.cloud import bigquery

def get_db_client() -> bigquery.Client:
    """BigQueryクライアントを取得します。"""
    # TODO: プロジェクトIDや認証情報を環境変数から読み込む
    return bigquery.Client()
