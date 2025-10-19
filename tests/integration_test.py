import requests
import pytest
import psycopg2
import os
import json

def test_youtube_api_response(airflow_variable):
    api_key = airflow_variable("API_KEY")
    channel_handle = airflow_variable("CHANNEL_HANDLE")

    # url youtube
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"

    try:
        response = requests.get(url)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    except requests.RequestException as e:
        pytest.fail(f"Request to YouTube API failed: {e}")

# test data warehouse connection using real environment variables
def test_real_postgres_connection(real_postgres_conn_vars):
    cur = None

    try:
        cur = real_postgres_conn_vars.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        assert result == (1,), "Expected (1,) but got {}".format(result)

    except psycopg2.Error as e:
        pytest.fail(f"Database operation failed: {e}")
    finally:
        if cur:
            cur.close()
        if real_postgres_conn_vars:
            real_postgres_conn_vars.close()

# test if API extraction task produced a JSON file
def test_api_to_json():
    """TEST if the API extraction task produced a JSON file with data"""
    json_path = "/opt/airflow/data/YT_data_2025-10-19.json"
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0, "JSON file is empty"
            assert "video_id" in data[0], "Expected key 'video_id' not found in JSON data"
    
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to decode JSON file: {e}")

# Test if JSON data successfully loaded into Postgres staging table
def test_json_to_postgres(real_postgres_conn_vars):
    """Test if JSON data successfully loaded into Postgres staging table"""
    cur = None

    try:
        cur = real_postgres_conn_vars.cursor()
        cur.execute('SELECT COUNT(*) FROM staging.yt_api;')
        row_count = cur.fetchone()[0]
        assert row_count > 0, "No data found in staging.yt_api table"

    except psycopg2.Error as e:
        pytest.fail(f"Database operation failed: {e}")
    finally:
        if cur:
            cur.close()
        if real_postgres_conn_vars:
            real_postgres_conn_vars.close()

# Test if data transformed and loaded into Postgres core table
def test_transform_load_postgres(real_postgres_conn_vars):
    """Test if data transformed and loaded into Postgres core table"""
    cur = None

    try:
        cur = real_postgres_conn_vars.cursor()
        cur.execute('SELECT COUNT(*) FROM core.yt_api;')
        row_count = cur.fetchone()[0]
        assert row_count > 0, "No data found in core.yt_api table"

    except psycopg2.Error as e:
        pytest.fail(f"Database operation failed: {e}")
    finally:
        if cur:
            cur.close()
        if real_postgres_conn_vars:
            real_postgres_conn_vars.close()