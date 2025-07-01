import pytest
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
from documentation_parser import (
    parse_has_project_id_scope,
    parse_required_role,
    parse_table_name,
    update_column_list,
    extract_partitioning_key,
    generate_yml,
)
from sql_generator import generate_sql

# Get the root directory (parent of tests)
ROOT_DIR = Path(__file__).parent.parent
TESTS_DIR = Path(__file__).parent


def test_parse_required_role():
    # Test case: Required role is present
    with open(ROOT_DIR / "html_content.html", "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    result = parse_required_role(soup)
    with open(TESTS_DIR / "html_content_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected

    # Test case: Required role is present (second case)
    with open(ROOT_DIR / "html_content_2.html", "r") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    result = parse_required_role(soup)
    with open(TESTS_DIR / "html_content_2_expected.sql", "r") as file:
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
    with open(ROOT_DIR / "html_content.html", "r") as file:
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
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
    )
    with open(TESTS_DIR / "test_generate_sql_table_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_table_no_project_id():
    # Test generate_sql function
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=False,
    )
    with open(
        TESTS_DIR / "test_generate_sql_table_no_project_id_expected.sql", "r"
    ) as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_dataset():
    # Test generate_sql function
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "dataset",
        has_project_id_scope=True,
    )
    with open(TESTS_DIR / "test_generate_sql_dataset_expected.sql", "r") as file:
        expected = file.read()
        assert result == expected


def test_extract_partitioning_key():
    # Test case 1: Partitioning key and clustering in paragraph format (working case)
    html_content = """
    <p>The underlying data is partitioned by the <code translate="no" dir="ltr">creation_time</code> column and clustered
    by <code translate="no" dir="ltr">project_id</code> and <code translate="no" dir="ltr">user_email</code>.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "creation_time"
    assert clustering_columns == ["project_id", "user_email"]

    # Test case 2: Partitioning key and clustering (different partition key)
    html_content = """
    <p>The underlying data is partitioned by the <code translate="no" dir="ltr">job_creation_time</code> column and clustered
    by <code translate="no" dir="ltr">project_id</code> and <code translate="no" dir="ltr">user_email</code>.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "job_creation_time"
    assert clustering_columns == ["project_id", "user_email"]

    # Test case 3: Only clustering, no partitioning (working case)
    html_content = """
    <p>The underlying data is clustered by <code translate="no" dir="ltr">project_id</code> and <code translate="no" dir="ltr">user_email</code>.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key is None
    assert clustering_columns == ["project_id", "user_email"]

    # Test case 4: Single clustering column (working case)
    html_content = """
    <p>The underlying data is clustered by <code translate="no" dir="ltr">project_id</code>.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key is None
    assert clustering_columns == ["project_id"]

    # Test case 5: No partitioning or clustering mentioned
    html_content = """
    <p>This is just some regular text without any partitioning or clustering information.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key is None
    assert clustering_columns == []

    # Test case 6: Special pattern matching for creation_time with project_id and user_email
    html_content = """
    <p>The table includes creation_time, project_id, and user_email columns.</p>
    <p>The underlying data is partitioned by the <code translate="no" dir="ltr">creation_time</code> column.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "creation_time"
    assert clustering_columns == ["project_id", "user_email"]

    # Test case 7: Special pattern matching for job_creation_time with project_id and user_email
    html_content = """
    <p>The table includes job_creation_time, project_id, and user_email columns.</p>
    <p>The underlying data is partitioned by the <code translate="no" dir="ltr">job_creation_time</code> column.</p>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    partitioning_key, clustering_columns = extract_partitioning_key(soup)
    assert partitioning_key == "job_creation_time"
    assert clustering_columns == ["project_id", "user_email"]


def test_generate_sql_table_with_partitioning_key():
    # Test generate_sql function with partitioning key
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
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
        enabled=True,
        tags=["test"],
    )
    with open(
        TESTS_DIR / "test_generate_sql_table_with_partitioning_key_expected.sql", "r"
    ) as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_table_with_custom_materialization():
    # Test generate_sql function with custom materialization and no project scoping
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=False,
        partitioning_key=None,
        materialization="view",
    )
    with open(
        TESTS_DIR / "test_generate_sql_table_with_custom_materialization_expected.sql",
        "r",
    ) as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_table_with_custom_materialization_and_project_scope():
    # Test generate_sql function with custom materialization and project scoping
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        partitioning_key=None,
        materialization="incremental",
    )
    with open(
        TESTS_DIR
        / "test_generate_sql_table_with_custom_materialization_and_project_scope_expected.sql",
        "r",
    ) as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_table_with_custom_materialization_and_partitioning():
    # Test generate_sql function with custom materialization, project scoping, and partitioning
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "data_type": "STRING", "description": "Field 3"},
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
        materialization="table",
    )
    with open(
        TESTS_DIR
        / "test_generate_sql_table_with_custom_materialization_and_partitioning_expected.sql",
        "r",
    ) as file:
        expected = file.read()
        assert result == expected


def test_generate_sql_table_with_enabled_false():
    # Test generate_sql function with enabled=false
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
        {"name": "field2", "data_type": "INTEGER", "description": "Field 2"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        enabled=False,
    )
    expected_config = "{{ config(materialized=dbt_bigquery_monitoring_materialization(), enabled=false) }}"
    assert expected_config in result


def test_generate_sql_table_with_tags_only():
    # Test generate_sql function with tags only
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        tags=["monitoring", "bigquery"],
    )
    expected_config = 'tags=["monitoring", "bigquery"]'
    assert expected_config in result


def test_generate_sql_table_with_enabled_and_tags():
    # Test generate_sql function with both enabled and tags
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        enabled=True,
        tags=["test", "development"],
    )
    # Check that both enabled and tags are in the config
    assert "enabled=true" in result
    assert 'tags=["test", "development"]' in result


def test_generate_sql_table_no_project_scope_with_enabled_tags():
    # Test that enabled and tags still work even without project scope
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=False,
        enabled=False,
        tags=["basic"],
    )
    # Should have a config block even without project scope
    assert "{{ config(" in result
    assert "enabled=false" in result
    assert 'tags=["basic"]' in result


def test_generate_yml():
    # Test generate_yml function with simple columns
    columns = [
        {"name": "field1", "type": "STRING", "description": "Field 1"},
        {"name": "field2", "type": "INTEGER", "description": "Field 2"},
        {"name": "field3", "type": "STRING", "description": "Field 3"},
    ]
    result = generate_yml("information_schema_test_table", columns)
    with open(TESTS_DIR / "test_generate_yml_expected.yml", "r") as file:
        expected = file.read()
        assert result == expected


def test_generate_yml_with_complex_columns():
    # Test generate_yml function with complex columns (including RECORD types)
    columns = [
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
    result = generate_yml("information_schema_test_table_with_complex_columns", columns)
    with open(
        TESTS_DIR / "test_generate_yml_with_complex_columns_expected.yml", "r"
    ) as file:
        expected = file.read()
        assert result == expected


def test_generate_yml_empty_columns():
    # Test generate_yml function with no columns
    columns = []
    result = generate_yml("information_schema_empty_table", columns)
    expected = """version: 2
models:
- name: information_schema_empty_table
  columns: []
"""
    assert result == expected


def test_generate_yml_special_characters_in_description():
    # Test generate_yml function with special characters in descriptions
    columns = [
        {
            "name": "special_field",
            "type": "STRING",
            "description": 'This field contains special characters: @#$%^&*()_+ and "quotes"',
        },
        {
            "name": "multiline_field",
            "type": "STRING",
            "description": "This is a\nmultiline description\nwith line breaks",
        },
    ]
    result = generate_yml("information_schema_special_table", columns)

    # Check that the result is valid YAML
    import yaml

    parsed = yaml.safe_load(result)
    assert parsed["version"] == 2
    assert len(parsed["models"]) == 1
    assert parsed["models"][0]["name"] == "information_schema_special_table"
    assert len(parsed["models"][0]["columns"]) == 2

    # Check specific field values
    columns_dict = {col["name"]: col for col in parsed["models"][0]["columns"]}
    assert (
        columns_dict["special_field"]["description"]
        == 'This field contains special characters: @#$%^&*()_+ and "quotes"'
    )
    assert (
        columns_dict["multiline_field"]["description"]
        == "This is a\nmultiline description\nwith line breaks"
    )


def test_generate_yml_integration_with_generate_files():
    # Test that generate_files creates proper YAML files
    # This is a mock test that doesn't actually make HTTP requests

    # Mock data that would normally come from parsing HTML
    test_columns = [
        {"name": "test_field1", "type": "STRING", "description": "Test field 1"},
        {"name": "test_field2", "type": "INTEGER", "description": "Test field 2"},
    ]

    # Test the generate_yml function with the same structure used in generate_files
    model_name = "information_schema_test_integration"
    result = generate_yml(model_name, test_columns)

    # Verify the structure
    import yaml

    parsed = yaml.safe_load(result)

    assert parsed["version"] == 2
    assert len(parsed["models"]) == 1

    model = parsed["models"][0]
    assert model["name"] == model_name
    assert len(model["columns"]) == 2

    # Verify column structure
    columns = {col["name"]: col for col in model["columns"]}
    assert "test_field1" in columns
    assert "test_field2" in columns
    assert columns["test_field1"]["data_type"] == "STRING"
    assert columns["test_field1"]["description"] == "Test field 1"
    assert columns["test_field2"]["data_type"] == "INTEGER"
    assert columns["test_field2"]["description"] == "Test field 2"


def test_yml_indentation_format():
    # Test that the YAML output has proper indentation (2 spaces)
    columns = [
        {"name": "field1", "type": "STRING", "description": "Field 1"},
        {"name": "field2", "type": "INTEGER", "description": "Field 2"},
    ]
    result = generate_yml("test_model", columns)

    lines = result.split("\n")

    # Check specific indentation patterns
    assert lines[0] == "version: 2"  # No indentation for top level
    assert lines[1] == "models:"  # No indentation for top level
    assert lines[2] == "- name: test_model"  # No leading spaces for list item
    assert lines[3] == "  columns:"  # 2 spaces
    assert lines[4] == "  - name: field1"  # 2 spaces for nested list item
    assert lines[5] == "    description: Field 1"  # 4 spaces for nested content
    assert lines[6] == "    data_type: STRING"  # 4 spaces for nested content


def test_yml_special_characters_handling():
    # Test that YAML properly handles special characters and multiline descriptions
    columns = [
        {
            "name": "special_chars",
            "type": "STRING",
            "description": 'Field with special chars: @#$%^&*()_+ and "quotes"',
        },
        {
            "name": "multiline_desc",
            "type": "STRING",
            "description": "Line 1\nLine 2\nLine 3",
        },
    ]
    result = generate_yml("test_special", columns)

    # Parse the YAML to ensure it's valid
    import yaml

    parsed = yaml.safe_load(result)

    # Verify the special characters and multiline content are preserved
    columns_dict = {col["name"]: col for col in parsed["models"][0]["columns"]}

    assert (
        columns_dict["special_chars"]["description"]
        == 'Field with special chars: @#$%^&*()_+ and "quotes"'
    )
    assert columns_dict["multiline_desc"]["description"] == "Line 1\nLine 2\nLine 3"


def test_generate_sql_config_parameter_order():
    # Test that config parameters appear in the expected order:
    # materialized, enabled, tags, partition_by, partition_expiration_days
    columns = [
        {"name": "field1", "data_type": "STRING", "description": "Field 1"},
    ]
    result = generate_sql(
        "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        columns,
        "jobs",
        "jobs.admin",
        "table",
        has_project_id_scope=True,
        partitioning_key="creation_time",
        enabled=True,
        tags=["test", "monitoring"],
    )

    # Find the config line
    config_line = None
    for line in result.split("\n"):
        if line.strip().startswith("{{ config("):
            config_line = line.strip()
            break

    assert config_line is not None
    # Check that the parameters appear in the expected order
    materialized_pos = config_line.find("materialized=")
    enabled_pos = config_line.find("enabled=")
    tags_pos = config_line.find("tags=")
    partition_pos = config_line.find("partition_by=")

    # All should be found
    assert materialized_pos != -1
    assert enabled_pos != -1
    assert tags_pos != -1
    assert partition_pos != -1

    # Check order: materialized < enabled < tags < partition_by
    assert materialized_pos < enabled_pos
    assert enabled_pos < tags_pos
    assert tags_pos < partition_pos


def test_update_column_list_with_field_mappings():
    # Test field mappings work correctly
    columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {
            "name": "secondaryLocation",
            "type": "STRING",
            "description": "Secondary location",
        },
        {
            "name": "originalPrimaryLocation",
            "type": "STRING",
            "description": "Original primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    field_mappings = {
        "primaryLocation": "primary_location",
        "secondaryLocation": "secondary_location",
        "originalPrimaryLocation": "original_primary_location",
    }

    result = update_column_list(
        columns, exclude_columns=[], field_mappings=field_mappings
    )

    expected_columns = [
        {
            "name": "primary_location",
            "type": "STRING",
            "description": "Primary location",
        },
        {
            "name": "secondary_location",
            "type": "STRING",
            "description": "Secondary location",
        },
        {
            "name": "original_primary_location",
            "type": "STRING",
            "description": "Original primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    assert result == expected_columns


def test_update_column_list_with_field_mappings_and_exclusions():
    # Test field mappings work with column exclusions
    columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "excludeMe", "type": "STRING", "description": "Column to exclude"},
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    field_mappings = {
        "primaryLocation": "primary_location",
    }

    exclude_columns = ["excludeme"]  # Note: exclusion is case-insensitive

    result = update_column_list(
        columns, exclude_columns=exclude_columns, field_mappings=field_mappings
    )

    expected_columns = [
        {
            "name": "primary_location",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    assert result == expected_columns


def test_update_column_list_with_field_mappings_and_struct_columns():
    # Test field mappings work with struct columns (nested columns)
    columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {
            "name": "struct_col.sub1",
            "type": "STRING",
            "description": "Struct subcolumn 1",
        },
        {
            "name": "struct_col.sub2",
            "type": "INTEGER",
            "description": "Struct subcolumn 2",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    field_mappings = {
        "primaryLocation": "primary_location",
    }

    result = update_column_list(
        columns, exclude_columns=[], field_mappings=field_mappings
    )

    expected_columns = [
        {
            "name": "primary_location",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
        {
            "name": "struct_col",
            "type": "RECORD",
            "description": "struct_col.sub1 : Struct subcolumn 1\nstruct_col.sub2 : Struct subcolumn 2",
        },
    ]

    assert result == expected_columns


def test_update_column_list_field_mappings_none():
    # Test that None field_mappings parameter works correctly (backward compatibility)
    columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    result = update_column_list(columns, exclude_columns=[], field_mappings=None)

    # Without field mappings, column names should remain unchanged
    expected_columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    assert result == expected_columns


def test_update_column_list_field_mappings_empty():
    # Test that empty field_mappings dict works correctly
    columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    result = update_column_list(columns, exclude_columns=[], field_mappings={})

    # With empty field mappings, column names should remain unchanged
    expected_columns = [
        {
            "name": "primaryLocation",
            "type": "STRING",
            "description": "Primary location",
        },
        {"name": "normalColumn", "type": "STRING", "description": "A normal column"},
    ]

    assert result == expected_columns
