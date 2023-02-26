dependencies:
	pipenv lock -r > requirements.txt

run.server:
	flask --app app run --host=0.0.0.0 --port=4000 --reload