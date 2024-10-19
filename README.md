# dbt bigquery monitoring parser

This repository contains a tool to generate dbt model from INFORMATION_SCHEMA tables from BigQuery using the public documentation.
It's written in Python and parse the documentation  from <https://cloud.google.com/bigquery/docs/>.
The models are then used in <https://github.com/bqbooster/dbt-bigquery-monitoring>.

## Usage

Assuming you have Python and conda installed:

```bash
make setup_environment
make activate_environment
make run
```

And then the models will be generated in the `output` folder.

If you don't have conda installed, you can use pip to install the dependencies using the requirements.txt with:

```bash
pip install -r requirements.txt
```
