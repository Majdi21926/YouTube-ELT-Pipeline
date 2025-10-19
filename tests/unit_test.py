

# test_api_key
def test_api_key(api_key):
    assert api_key == "MOCK_KEY1234"

# test_channel_handle
def test_channel_handle(channel_handle):
    assert channel_handle == "MOCK_CHANNEL"

# test_mock_postgres_conn_vars
def test_mock_postgres_conn_vars(mock_postgres_conn_vars):
    assert mock_postgres_conn_vars.login == "mock_username"
    assert mock_postgres_conn_vars.password == "mock_password"
    assert mock_postgres_conn_vars.host == "mock_host"
    assert mock_postgres_conn_vars.port == 1234
    assert mock_postgres_conn_vars.schema == "mock_db_name"

# test_dagbag
def test_dagbag(dagbag):
    """  
    This test will test the integrity of our DAGs in 4 integrities:
    1. There will be no import errors.
    2. The DAGs are being loaded.
    3. The number of the DAGs is correct.
    4. Each DAG has a number of tasks we expect
    """
    # 1. 
    assert dagbag.import_errors == {}, f"DAG import errors: {dagbag.import_errors}"
    print("====================================")
    print(dagbag.import_errors)
    print("====================================")

    # 2.
    expected_dag_ids = ["produce_json", "etl_warehouse", "data_quality"]
    loaded_dag_ids = list(dagbag.dags.keys())
    print("====================================")
    print(dagbag.dags.keys())
    for dag_id in expected_dag_ids:
        assert dag_id in loaded_dag_ids, f"DAG {dag_id} is not loaded"
    
    print("====================================")
    # 3.
    #assert len(loaded_dag_ids) == 3, f"Expected 3 DAGs, but found {len(loaded_dag_ids)}"
    assert dagbag.size() == 3
    print(dagbag.size())

    print("====================================")
    # 4.
    expected_tasks_count = {
        "produce_json": 4,
        "etl_warehouse": 2,
        "data_quality": 2
    }
    for dag_id, dag in dagbag.dags.items():
        expected_count = expected_tasks_count[dag_id]
        actual_count = len(dag.tasks)
        assert actual_count == expected_count, f"DAG {dag_id} has {actual_count} tasks, expected {expected_count}"
        print(dag_id, len(dag.tasks))


