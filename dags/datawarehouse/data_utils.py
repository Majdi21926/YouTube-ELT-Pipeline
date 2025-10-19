from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor

table = "yt_api"

# get_conn_cursor
def get_conn_cursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="elt_db")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor) # RealDictCursor is used because it changes how the data is returned
    return conn, cur

def close_conn_cursor(conn, cur):
    cur.close()
    conn.close()

# create schema
def create_schema(schema):
    conn, cur  = get_conn_cursor()
    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"
    cur.execute(schema_sql)
    conn.commit()
    close_conn_cursor(conn, cur)

# create table
def create_table(schema):
    conn, cur = get_conn_cursor()

    if schema == "staging":
        table_sql = f"""
                CREATE TABLE IF NOT EXISTS {schema}.{table} (
                    "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                    "Video_Title" TEXT NOT NULL,
                    "Upload_Date" TIMESTAMP NOT NULL,
                    "Duration" VARCHAR(20) NOT NULL,
                    "Video_Views" INT,
                    "Likes_Count" INT,
                    "Comments_Count" INT   
                );
        """
    else:
        table_sql = f"""
                CREATE TABLE IF NOT EXISTS {schema}.{table} (
                    "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                    "Video_Title" TEXT NOT NULL,
                    "Upload_Date" TIMESTAMP NOT NULL,
                    "Duration" TIME NOT NULL,
                    "Video_Type" VARCHAR(20) NOT NULL,
                    "Video_Views" INT,
                    "Likes_Count" INT,
                    "Comments_Count" INT   
                );
        """
    cur.execute(table_sql)
    conn.commit()
    close_conn_cursor(conn, cur)

# get video ids already in the table
def get_video_ids(cur, schema):
    video_ids_sql = f"SELECT \"Video_ID\" FROM {schema}.{table};"
    cur.execute(video_ids_sql)
    ids = cur.fetchall()
    video_ids = [id["Video_ID"] for id in ids] # id is a dictionary because of RealDictCursor
    return video_ids