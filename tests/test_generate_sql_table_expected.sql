
      {# More details about base table in https://cloud.google.com/bigquery/docs/information-schema-jobs -#}
      jobs.admin
      WITH base AS (
      {% if project_list()|length > 0 -%}
          SELECT field1, field2, field3
          FROM `region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`jobs`
          WHERE project_id IN (
          {% for project in project_list() -%}
          '{{ project | trim }}'
          {% if not loop.last %},{% endif %}
          {% endfor %}
          )
      {%- else %}
          SELECT field1, field2, field3
          FROM `region-{{ var('bq_region') }}`.`INFORMATION_SCHEMA`.`jobs`
      {%- endif %}
      )
      SELECT
      field1, field2, field3,
      FROM
      base
      