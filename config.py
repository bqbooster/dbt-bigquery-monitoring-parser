pages_to_process = {
    # Access Control
    "object_privileges": {
        "dir": "access_control",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-object-privileges",
        "exclude_columns": ["privlege_type"],
        "materialization": "ephemeral",
    },
    # BI Engine
    "bi_capacities": {
        "dir": "bi_engine",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-bi-capacities",
    },
    "bi_capacity_changes": {
        "dir": "bi_engine",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-bi-capacity-changes",
    },
    # configuration
    "effective_project_options": {
        "dir": "configuration",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-effective-project-options",
    },
    "organization_options": {
        "dir": "configuration",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-organization-options",
    },
    "organization_options_changes": {
        "dir": "configuration",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-organization-options-changes",
    },
    "project_options": {
        "dir": "configuration",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-project-options",
    },
    "project_options_changes": {
        "dir": "configuration",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-project-options-changes",
    },
    # datasets
    "schemata_options": {
        "dir": "datasets",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-datasets-schemata-options",
    },
    "schemata": {
        "dir": "datasets",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-datasets-schemata",
    },
    "schemata_links": {
        "dir": "datasets",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-datasets-schemata-links",
    },
    "shared_dataset_usage": {
        "dir": "datasets",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-shared-dataset-usage",
    },
    "schemata_replicas": {
        "dir": "datasets",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-schemata-replicas",
    },
    "schemata_replicas_by_failover_reservation": {
        "dir": "datasets",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-schemata-replicas-by-failover-reservation",
    },
    # Jobs
    "jobs": {
        "dir": "jobs",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        "exclude_columns": ["query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    "jobs_by_project": {
        "dir": "jobs",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs",
        "override_table_name": "JOBS_BY_PROJECT",
        "exclude_columns": ["query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    "jobs_by_user": {
        "dir": "jobs",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-by-user",
        "exclude_columns": ["query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    "jobs_by_folder": {
        "tags": ["dbt-bigquery-monitoring-information-schema-by-folder"],
        "enabled": False,
        "dir": "jobs",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-by-folder",
        "exclude_columns": ["query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    "jobs_by_organization": {
        "dir": "jobs",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-by-organization",
        "exclude_columns": ["query", "query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    # jobs timeline
    "jobs_timeline": {
        "dir": "jobs_timeline",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-timeline",
        "exclude_columns": ["query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    "jobs_timeline_by_user": {
        "dir": "jobs_timeline",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-timeline-by-user",
        "exclude_columns": ["query_info.resource_warning", "query_info.query_hashes.normalized_literals", "query_info.performance_insights", "query_info.optimization_details", "folder_numbers"],
    },
    "jobs_timeline_by_folder": {
        "tags": ["dbt-bigquery-monitoring-information-schema-by-folder"],
        "enabled": False,
        "dir": "jobs_timeline",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-timeline-by-folder",
    },
    "jobs_timeline_by_organization": {
        "dir": "jobs_timeline",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-jobs-timeline-by-organization",
    },
    # recommendations and insights
    "insights": {
        "dir": "recommendations_and_insights",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-insights",
    },
    "recommendations": {
        "dir": "recommendations_and_insights",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-recommendations",
    },
    "recommendations_by_organization": {
        "dir": "recommendations_and_insights",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-recommendations-by-org",
    },
    # reservations
    "assignments": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-assignments",
    },
    "assignment_changes": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-assignments-changes",
    },
    "capacity_commitments": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-capacity-commitments",
    },
    "capacity_commitment_changes": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-capacity-commitment-changes",
    },
    "reservations": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-reservations",
    },
    "reservation_changes": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-reservation-changes",
    },
    "reservations_timeline": {
        "dir": "reservations",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-reservation-timeline",
    },
    # Routines
    "parameters": {
        "dir": "routines",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-parameters",
    },
    "routines": {
        "dir": "routines",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-routines",
        "project-prefix": False,
    },
    "routine_options": {
        "dir": "routines",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-routine-options",
    },
    # search indexes
    "search_indexes": {
        "type": "dataset",
        "dir": "search_indexes",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-indexes",
    },
    "search_index_columns": {
        "type": "dataset",
        "dir": "search_indexes",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-index-columns",
    },
    # sessions
    "sessions_by_project": {
        "dir": "sessions",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-sessions-by-project",
    },
    "sessions_by_user": {
        "dir": "sessions",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-sessions-by-user",
        "exclude_columns": ["principal_subject"],
    },
    # streaming
    "streaming_timeline": {
        "dir": "streaming",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-streaming",
    },
    "streaming_timeline_by_folder": {
        "tags": ["dbt-bigquery-monitoring-information-schema-by-folder"],
        "enabled": False,
        "dir": "streaming",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-streaming-by-folder",
    },
    "streaming_timeline_by_organization": {
        "dir": "streaming",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-streaming-by-organization",
    },
    # tables
    "columns": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-columns",
    },
    "column_field_paths": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-column-field-paths",
    },
    "constraint_column_usage": {
        "type": "dataset",
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-constraint-column-usage",
    },
    "key_column_usage": {
        "type": "dataset",
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-key-column-usage",
    },
    # partitions is per dataset
    "partitions": {
        "type": "dataset",
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-partitions"
    },
    "tables": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-tables",
    },
    "table_options": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-table-options",
    },
    "table_constraints": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-table-constraints",
    },
    "table_snapshots": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-snapshots",
    },
    "table_storage": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-table-storage",
    },
    "table_storage_by_organization": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-table-storage-by-organization",
    },
    "table_storage_usage_timeline": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-table-storage-usage",
    },
    "table_storage_usage_timeline_by_organization": {
        "dir": "tables",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-table-storage-usage-by-organization",
    },
    # vector indexes
    "vector_indexes": {
        "dir": "vector_indexes",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-vector-indexes",
    },
    "vector_index_columns": {
        "dir": "vector_indexes",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-vector-index-columns",
    },
    "vector_index_options": {
        "dir": "vector_indexes",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-vector-index-options",
    },
    # views
    "views": {
        "dir": "views",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-views",
    },
    "materialized_views": {
        "dir": "views",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-materialized-views",
    },
    # Write API
    "write_api_timeline": {
        "dir": "write_api",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-write-api",
    },
    "write_api_timeline_by_folder": {
        "tags": ["dbt-bigquery-monitoring-information-schema-by-folder"],
        "enabled": False,
        "dir": "write_api",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-write-api-by-folder",
    },
    "write_api_timeline_by_organization": {
        "dir": "write_api",
        "url": "https://cloud.google.com/bigquery/docs/information-schema-write-api-by-organization",
    },
}
