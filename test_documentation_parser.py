import pytest
from bs4 import BeautifulSoup
from documentation_parser import (
    parse_has_project_id_scope,
    parse_required_role,
    parse_table_name,
    update_column_list,
    extract_partitioning_key,
)
from sql_generator import generate_sql


def test_parse_required_role():
    # Test case: Required role is present
    with open("html_content.html", "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    result = parse_required_role(soup)
    with open("tests/html_content_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected

    # Test case: Required role is present (second case)
    with open("html_content_2.html", "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    result = parse_required_role(soup)
    with open("tests/html_content_2_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected

    # Test case: Required role is not present
    html_content = """
    <h2 id="other_role" data-text="Other role" tabindex="-1" role="presentation">
        <span class="devsite-heading" role="heading" aria-level="2">Other role</span>
        <button type="button" class="devsite-heading-link button-flat material-icons" aria-label="Copy link to this section: Other role" data-title="Copy link to this section: Other role" data-id="other_role"></button>
    </h2>
    <p>
        This is some other role.
    </p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    assert parse_required_role(soup) is None


def test_parse_table_name():
    # Test case: Table name is present
    with open("html_content.html", "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    result = parse_table_name(soup)
    expected = "OBJECT_PRIVILEGES"
    assert result == expected

    # Test case: Table name is not present
    html_content = """
  <td>
    <code>RANDOM_STRING.COLUMNS</code>
  </td>
  """
    soup = BeautifulSoup(html_content, "html.parser")
    result = parse_table_name(soup)
    assert result is None


def test_parse_has_project_id():
    # Test case: PROJECT_ID is present
    html_content = """
    <p>Optional: <code translate="no" dir="ltr"><var translate="no">PROJECT_ID</var></code>: the ID of your
    Google Cloud project. If not specified, the default project is used.

    </p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    assert parse_has_project_id_scope(soup) is True

    # Test case: PROJECT_ID is not present
    html_content = """
    <ul><li><code translate="no" dir="ltr"><var translate="no">REGION</var></code>: any <a href="/bigquery/docs/locations">dataset region name</a>. For example, <code translate="no" dir="ltr">US</code>, or <code translate="no" dir="ltr">us-west2</code>.</li></ul>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    assert parse_has_project_id_scope(soup) is False


def test_update_column_list():
    # Test case: Columns with exclude_columns
    columns = [
        {"name": "column1", "type": "STRING", "description": "Column 1"},
        {"name": "column2", "type": "INTEGER", "description": "Column 2"},
        {
            "name": "column4.subcolumn1",
            "type": "STRING",
            "description": "Subcolumn 1 of Column 4",
        },
        {
            "name": "column3.subcolumn1",
            "type": "STRING",
            "description": "Subcolumn 1 of Column 3",
        },
        {
            "name": "column3.subcolumn2",
            "type": "INTEGER",
            "description": "Subcolumn 2 of Column 3",
        },
    ]
    exclude_columns = ["column2", "column3.subcolumn1"]
    result = update_column_list(columns, exclude_columns)
    expected_columns = [
        {"name": "column1", "type": "STRING", "description": "Column 1"},
        {
            "name": "column3",
            "type": "RECORD",
            "description": "column3.subcolumn1 : Subcolumn 1 of Column 3\ncolumn3.subcolumn2 : Subcolumn 2 of Column 3",
        },
        {
            "name": "column4",
            "type": "RECORD",
            "description": "column4.subcolumn1 : Subcolumn 1 of Column 4",
        },
    ]
    assert result == expected_columns

    # Test case: Columns without exclude_columns
    columns = [
        {"name": "column1", "type": "STRING", "description": "Column 1"},
        {"name": "column2", "type": "INTEGER", "description": "Column 2"},
        {
            "name": "column3.subcolumn1",
            "type": "STRING",
            "description": "Subcolumn 1 of Column 3",
        },
        {
            "name": "column3.subcolumn2",
            "type": "INTEGER",
            "description": "Subcolumn 2 of Column 3",
        },
    ]
    exclude_columns = []
    result = update_column_list(columns, exclude_columns)
    expected_columns = [
        {"name": "column1", "type": "STRING", "description": "Column 1"},
        {"name": "column2", "type": "INTEGER", "description": "Column 2"},
        {
            "name": "column3",
            "type": "RECORD",
            "description": "column3.subcolumn1 : Subcolumn 1 of Column 3\ncolumn3.subcolumn2 : Subcolumn 2 of Column 3",
        },
    ]
    assert result == expected_columns

    # Test case: Columns with exclude_columns (second case)
    columns = [
        {"name": "column1", "type": "STRING", "description": "Column 1"},
        {"name": "column2", "type": "INTEGER", "description": "Column 2"},
        {
            "name": "column3.subcolumn1",
            "type": "STRING",
            "description": "Subcolumn 1 of Column 3",
        },
        {
            "name": "column3.subcolumn2",
            "type": "INTEGER",
            "description": "Subcolumn 2 of Column 3",
        },
    ]
    exclude_columns = ["column1", "column2"]
    result = update_column_list(columns, exclude_columns)
    expected_columns = [
        {
            "name": "column3",
            "type": "RECORD",
            "description": "column3.subcolumn1 : Subcolumn 1 of Column 3\ncolumn3.subcolumn2 : Subcolumn 2 of Column 3",
        },
    ]
    assert result == expected_columns


def test_generate_sql_table():
    # Test generate_sql function
    columns = [
        {"name": "field1", "type": "STRING", "description": "Field 1"},
        {"name": "field2", "type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
    )
    with open("tests/test_generate_sql_table_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_table_no_project_id():
    # Test generate_sql function
    columns = [
        {"name": "field1", "type": "STRING", "description": "Field 1"},
        {"name": "field2", "type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=False,
    )
    with open("tests/test_generate_sql_table_no_project_id_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_dataset():
    # Test generate_sql function
    columns = [
        {"name": "field1", "type": "STRING", "description": "Field 1"},
        {"name": "field2", "type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "dataset",
        has_project_id_scope=True,
    )
    with open("tests/test_generate_sql_dataset_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected


def test_extract_partitioning_key():
    # Test case: Partitioning key and clustering in paragraph format
    html_content = """
    <p>The underlying data is partitioned by the <code translate="no" dir="ltr">creation_time</code> column and clustered
    by <code translate="no" dir="ltr">project_id</code> and <code translate="no" dir="ltr">user_email</code>.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "creation_time"
    assert clustering_columns == ["project_id", "user_email"]

    # Test case: Partitioning key and clustering in aside note format
    html_content = """
    <aside class="note"><strong>Note:</strong><span> The underlying data is partitioned by the <code translate="no" dir="ltr">job_creation_time</code> column and
    clustered by <code translate="no" dir="ltr">project_id</code> and <code translate="no" dir="ltr">user_email</code>.</span></aside>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "job_creation_time"
    assert clustering_columns == ["project_id", "user_email"]

    # Test case: Only partitioning key, no clustering
    html_content = """
    <p>The underlying data is partitioned by the <code translate="no" dir="ltr">creation_time</code> column.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "creation_time"
    assert clustering_columns == []

    # Test case: Only clustering, no partitioning
    html_content = """
    <p>The underlying data is clustered by <code translate="no" dir="ltr">project_id</code>.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key is None
    assert clustering_columns == ["project_id"]

    # Test case: No partitioning or clustering
    html_content = "<p>Some random text.</p>"
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key is None
    assert clustering_columns == []

    # Test case: Partitioning mentioned but no key can be extracted
    html_content = """
    <p>The underlying data is partitioned by the column.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with pytest.raises(ValueError, match="Partitioning is mentioned but no partitioning key could be extracted"):
        extract_partitioning_key(soup)

    # Test case: Clustering mentioned but no columns can be extracted
    html_content = """
    <p>The underlying data is clustered by some columns.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with pytest.raises(ValueError, match="Clustering is mentioned but no clustering columns could be extracted"):
        extract_partitioning_key(soup)


def test_generate_sql_table_with_partitioning_key():
    # Test generate_sql function with partitioning key
    columns = [
        {"name": "field1", "type": "STRING", "description": "Field 1"},
        {"name": "field2", "type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "type": "STRING", "description": "Field 3"},
    ]
    partitioning_key = "creation_time"
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        partitioning_key=partitioning_key,
    )
    with open(
        "tests/test_generate_sql_table_with_partitioning_key_expected.sql", "r"
    ) as file:
        expected = file.read()
        assert result == expected
