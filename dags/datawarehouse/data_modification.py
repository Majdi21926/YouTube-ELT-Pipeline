import logging

logger = logging.getLogger(__name__) # handling logging in the scripts
table = "yt_api"


# we insert the API data we load it from the JSON file into the staging and core tables
def insert_rows(cur, conn, schema, row):
    
    try:

        if schema == "staging":

            video_id = 'video_id' # for logging purpose
            # We define the columns where we will insert the data
            insert_sql = f"""
                INSERT INTO {schema}.{table}("Video_ID", "Video_Title", "Upload_Date", "Duration", "Video_Views", "Likes_Count", "Comments_Count")
                VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s); 
            """
            cur.execute(insert_sql, row)

        else:
            video_id = 'Video_ID' # for logging purpose # In this case, the name is Video_ID which is the same as in the staging table
            # We define the columns where we will insert the data
            insert_sql = f"""
                INSERT INTO {schema}.{table}("Video_ID", "Video_Title", "Upload_Date", "Duration", "Video_Type", "Video_Views", "Likes_Count", "Comments_Count")
                VALUES (%(Video_ID)s, %(Video_Title)s, %(Upload_Date)s, %(Duration)s, %(Video_Type)s, %(Video_Views)s, %(Likes_Count)s, %(Comments_Count)s) 
            """
            cur.execute(insert_sql, row)
        
        conn.commit()
        logger.info(f"Inserted row for video ID: {row[video_id]}")


    except Exception as e:
        logger.error(f"Error inserting row {row[video_id]}: {e}")
        raise e
    

# update rows
def update_rows(cur, conn, schema, row):

    try:
        # staging
        if schema == "staging":
            video_id = "video_id"
            upload_date = "publishedAt"
            video_title = "title"
            video_views = "viewCount"
            likes_count = "likeCount"
            comments_count = "commentCount"

        # core
        else:
            video_id = "Video_ID"
            upload_date = "Upload_Date"
            video_title = "Video_Title"
            video_views = "Video_Views"
            likes_count = "Likes_Count"
            comments_count = "Comments_Count"
        
        # Video_ID and Upload_Date are the natural keys, they won't change
        cur.execute(f"""
            UPDATE {schema}.{table}
            SET "Video_Title" = %({video_title})s,
                "Video_Views" = %({video_views})s,
                "Likes_Count" = %({likes_count})s,
                "Comments_Count" = %({comments_count})s
            WHERE "Video_ID" = %({video_id})s AND "Upload_Date" = %({upload_date})s;
        """, row
        )

        conn.commit()
        logger.info(f"Updated row for video ID: {row[video_id]}")

    except Exception as e:
        logger.error(f"Error updating row {row[video_id]}: {e}")
        raise e

# delete rows
def delete_rows(cur, conn, schema, video_ids):

    # convert video_ids to a proper SQL format string
    try:
        ids_str = ', '.join(f"'{vid}'" for vid in video_ids)
        delete_sql = f"DELETE FROM {schema}.{table} WHERE \"Video_ID\" IN ({ids_str});"
        cur.execute(delete_sql)
        conn.commit()
        logger.info(f"Deleted rows for video IDs: {ids_str}")
    
    except Exception as e:
        logger.error(f"Error deleting rows for video IDs {ids_str}: {e}")
        raise e