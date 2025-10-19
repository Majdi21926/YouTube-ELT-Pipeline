# This is the script that will handle the data modification in the data warehouse: create, insert, update, delete, tranform
import logging
logger = logging.getLogger(__name__) # handling logging in the scripts
table = "yt_api"

from airflow.decorators import task
from datawarehouse.data_utils import get_conn_cursor, close_conn_cursor, create_schema, create_table, get_video_ids
from datawarehouse.data_loading import load_data
from datawarehouse.data_transformation import transform_data
from datawarehouse.data_modification import insert_rows, update_rows, delete_rows

# function to create the staging table into the datawarehouse in postgres
@task
def staging_table():

    # define schema variable
    schema = "staging"
    # initialize the connection and cursor
    conn, cur = None, None
    try:

        conn, cur = get_conn_cursor()
        # we load the raw data, extrcated from the API and stored in a JSON file
        yt_data = load_data()
        # we create the schema if it does not exist
        create_schema(schema=schema)
        # we create the table if it does not exist
        create_table(schema=schema)
        # we get the video ids already in the table to avoid duplicates
        video_ids = get_video_ids(cur=cur, schema=schema)

        for row in yt_data:

            if len(video_ids) == 0:
                insert_rows(cur, conn, schema, row)
            else:
                if row['video_id'] not in video_ids:
                    insert_rows(cur, conn, schema, row)
                else:
                    update_rows(cur, conn, schema, row)
        
        # possible removal of videos by channel
        ids_in_json = {row['video_id'] for row in yt_data}
        #ids_in_db = {vid['Video_ID'] for vid in video_ids}
        ids_in_db = set(video_ids)
        ids_to_delete = ids_in_db - ids_in_json

        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info(f"Staging table {table} in schema {schema} created and data inserted/updated successfully.")
        close_conn_cursor(conn, cur)

    except Exception as e:
        logger.error(f"Error in staging_table: {e}")
        raise e
    
    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)

# function to create the core table into the datawarehouse in postgres: core table ontains transformed data retrieved from the staging table
@task
def core_table():

    # define schema variable
    schema = "core"
    # initialize the connection and cursor
    conn, cur = None, None
    try:

        conn, cur  = get_conn_cursor()
        # we create the schema if it does not exist
        create_schema(schema)
        # we create the table if it does not exist
        create_table(schema)
        # we get the video ids already in the table to avoid duplicates
        vide_ids  = get_video_ids(cur, schema)

        current_video_ids = set()
        # we get the data from the staging table
        cur.execute(f"SELECT * FROM staging.{table};")
        rows = cur.fetchall()
        # we transform the data and insert it into the core table
        for row in rows:

            current_video_ids.add(row['Video_ID'])

            if len(vide_ids) == 0:
                transformed_row = transform_data(row)
                insert_rows(cur, conn, schema, transformed_row)
            else:
                if row['Video_ID'] not in vide_ids:
                    transformed_row = transform_data(row)
                    insert_rows(cur, conn, schema, transformed_row)
                else:
                    transformed_row = transform_data(row)
                    update_rows(cur, conn, schema, transformed_row)
        
        # possible removal of videos by channel
        ids_in_db = set(vide_ids)
        ids_to_delete = ids_in_db - current_video_ids

        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)
        
        logger.info(f"Core table {table} in schema {schema} created and data inserted/updated successfully.")
    
    except Exception as e:
        logger.error(f"Error in core_table: {e}")
        raise e
    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)
    
            


