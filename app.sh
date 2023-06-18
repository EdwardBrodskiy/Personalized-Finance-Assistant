#!/bin/sh
PROJECT_ROOT="$(dirname $0)"
cd "$PROJECT_ROOT"
if [ -f venv/bin/activate ]; then
	source venv/bin/activate
	python app.py
else
	echo "Creating and installing requirements in venv."
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt &&
		python app.py
fi
