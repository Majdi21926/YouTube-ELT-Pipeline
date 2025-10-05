from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.video_stats import get_playlist_id, get_video_ids, extract_video_data, save_to_json

local_tz = pendulum.timezone("Europe/Paris")

default_args = {
    'owner': 'dataengineers',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'email': 'majdi.hbibi.7@gmail.com',
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    'start_date': pendulum.datetime(2025, 9, 25, tz=local_tz), # The DAG will running after the end of 1st January -- beginning of 2nd January
}

with DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='A simple DAG to extract YouTube video statistics and store them in JSON files',
    schedule='0 10 * * *', #Check crontab.guru
    catchup=False,
) as dag:
    
    # Define tasks
    playlist_id = get_playlist_id()
    video_id = get_video_ids(playlist_id)
    extract_video_details = extract_video_data(video_id)
    save_json = save_to_json(extract_video_details)

    # Set task dependencies
    playlist_id >> video_id >> extract_video_details >> save_json