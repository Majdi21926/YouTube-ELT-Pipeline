import os
from unittest import mock
from airflow.models import Variable, Connection, DagBag
import pytest

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