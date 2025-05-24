.PHONY: setup run clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && python app.py

clean:
	rm -rf .venv __pycache__ output/*.pdf output/*.json output/logs/*.log output/history.json
