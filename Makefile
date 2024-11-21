SHELL := /bin/bash

.PHONY: activate_environment setup_environment run

all: run

activate_environment:
	conda activate dbt-bigquery-monitoring-parser

setup_environment:
	conda create -n dbt-bigquery-monitoring-parser python=3.11 &&\
	conda activate dbt-bigquery-monitoring-parser &&\
	pip install beautifulsoup4 jinja2 requests

run:
	python documentation_parser.py all

#test using pytest
test:
	pytest test_documentation_parser.py

paste_buffer:
	# copy the contents of the buffer to a file
	pbpaste > temp.txt
	
# interprete line breaks to appropriate formatting
format_special:
	# replace \n with newline
	sed 's/\\n/\n/g' temp.txt > temp_fmt.txt.tmp && mv temp_fmt.txt.tmp temp_fmt.txt
	# replace escaped quotes with quotes
	sed "s/\\\'/\'/g" temp_fmt.txt > temp_fmt.txt.tmp && mv temp_fmt.txt.tmp temp_fmt.txt
	# replace escaped single quotes with single quotes
	sed 's/\\\"/\"/g' temp_fmt.txt > temp_fmt.txt.tmp && mv temp_fmt.txt.tmp temp_fmt.txt
