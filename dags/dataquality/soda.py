# This script is for base data quality logic for airflow DAG
import logging
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "pg_datasource"

# Function to create a Soda Check Operator
def yt_elt_data_quality(schema):

    try:
        task = BashOperator(
            task_id=f"soda_test_{schema}",
            bash_command=(
                f"soda scan -d {DATASOURCE} -c {SODA_PATH}/configuration.yml -v SCHEMA={schema} {SODA_PATH}/checks.yml"
            )
        )
        return task
    except Exception as e:
        logger.error(f"Error creating Soda Check Operator: {e} for schema: {schema}")
        raise