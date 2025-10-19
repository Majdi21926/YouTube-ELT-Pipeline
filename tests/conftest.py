import os
from unittest import mock
from airflow.models import Variable, Connection, DagBag
import pytest
import psycopg2

@pytest.fixture
def api_key():
    # handle dictionaries to mock the environment variable.
    with mock.patch.dict("os.environ", AIRFLOW_VAR_API_KEY="MOCK_KEY1234"): # It temprarily updates the environment dictionary with the key value
        yield Variable.get("API_KEY")  # This will return "MOCK_KEY1234"

# CHANNEL_HANDLE test fixture
@pytest.fixture
def channel_handle():
    with mock.patch.dict("os.environ", AIRFLOW_VAR_CHANNEL_HANDLE="MOCK_CHANNEL"):
        yield Variable.get("CHANNEL_HANDLE")  # This will return "MOCK_CHANNEL"


# DATABASE vas test fixture
@pytest.fixture
def mock_postgres_conn_vars():
    conn = Connection(
        login="mock_username",
        password="mock_password",
        host="mock_host",
        port=1234,
        schema="mock_db_name"
    )
    conn_uri = conn.get_uri()
    with mock.patch.dict("os.environ", AIRFLOW_CONN_POSTGRES_DB_YT_ELT=conn_uri):
        yield Connection.get_connection_from_secrets("postgres_db_yt_elt")

@pytest.fixture
def dagbag():
    yield DagBag()


# function will return the value of the varialbles from the environment by specific the variable name as an argument
@pytest.fixture
def airflow_variable():
    def get_airflow_variable(variable_name):
        env_var = f"AIRFLOW_VAR_{variable_name.upper()}"
        return os.getenv(env_var)
    
    return get_airflow_variable

# test the connection to the database that will store the ELT data with the real variables from the environment
@pytest.fixture
def real_postgres_conn_vars():
    dbname = os.getenv("ELT_DATABASE_NAME")
    user = os.getenv("ELT_DATABASE_USERNAME")
    password = os.getenv("ELT_DATABASE_PASSWORD")
    host = os.getenv("POSTGRES_CONN_HOST")
    port = os.getenv("POSTGRES_CONN_PORT")

    conn = None

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        yield conn

    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if conn is not None:
            conn.close()