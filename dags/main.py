from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.video_stats import get_playlist_id, get_video_ids, extract_video_data, save_to_json
from datawarehouse.datawarehouse import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

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

staging_schema = 'staging'
core_schema = 'core'

# DAG 1 : produce_json: to extract data from YouTube API and store it in JSON files
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

# DAG 2 : etl_datawarehouse: to create the staging and core tables in the datawarehouse and load data into them
with DAG(
    dag_id='etl_warehouse',
    default_args=default_args,
    description='A simple DAG to create staging and core tables in the datawarehouse and load data into them',
    schedule='0 11 * * *', #Check crontab.guru
    catchup=False,
) as dag2:

    # Define tasks
    staging = staging_table()
    core = core_table()

    # Set task dependencies
    staging >> core

# DAG 3 : data_quality: to perform data quality checks using Soda
with DAG(
    dag_id='data_quality',
    default_args=default_args,
    description='A simple DAG to perform data quality checks using Soda',
    schedule='0 12 * * *', #Check crontab.guru
    catchup=False,
) as dag3:
    
    data_quality_checks_staging = yt_elt_data_quality(staging_schema)
    data_quality_checks_core = yt_elt_data_quality(core_schema)

    data_quality_checks_staging >> data_quality_checks_core