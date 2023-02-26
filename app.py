from os import getenv
import logging

from flasgger import Swagger
from flask import Flask
from flask import request
from flask import jsonify
from pymongo import MongoClient
from pymongo.errors import OperationFailure


app = Flask(__name__)
swagger = Swagger(app)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

mongo_uri = getenv('MONGO_URI') if getenv('MONGO_URI') else "mongodb://mongo:secret@localhost:27017/"
db_name = getenv('MONGO_DATABASE') if getenv('MONGO_DATABASE') else "local"

client = MongoClient(mongo_uri)
database = client[db_name]

page_size = 20


@app.route("/health-check")
def health_check():
    """health-check endpoint
    ---
    tags:
        - health
    responses:
        200:
            description: OK
        500:
            description: INTERNAL SERVER ERROR
    """
    logger.info('health-check endpoint')
    try:
        client.server_info()
        return "OK", 200
    except OperationFailure:
        return "INTERNAL SERVER ERROR", 500


@app.route("/puntos-digitales", methods=['GET'])
def puntos_digitales():
    """puntos-digitales endpoint
    ---
    tags:
        - main
    parameters:
        - name: page
          in: query
          type: integer
          required: false
    responses:
        200:
            description: OK
    """
    logger.info('puntos-digitales endpoint')
    quantity = database['puntos-digitales'].count_documents({})

    try:
        page = int(request.args.get('page'))
    except TypeError:
        page = 1

    last_page = int(quantity/page_size) if quantity%page_size == 0 else int(quantity/page_size) + 1
    page = last_page if last_page < page else page
    data = database['puntos-digitales'].find({}, {'_id':0}).sort('id').skip((page-1)*page_size).limit(page_size)


    response = {
        'data': [ i for i in data ],
        'quantity': quantity,
        'current_page': page,
        'last_page': last_page
    }
    return jsonify(response)