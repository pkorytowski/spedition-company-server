import json

from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin

from Database import Database
from Utils import get_node_ids, get_nodes_list, get_most_valuable_freights, Case, get_best_case, dumper, ReturnCase

app = Flask(__name__)
CORS(app)
db = Database()


@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello World!'


@app.route('/cities')
@cross_origin()
def get_cities():
    cities = db.get_all_cities()
    response = Response(json.dumps(cities, default=dumper))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/freights')
@cross_origin()
def get_freights():
    freights = db.get_all_freights()
    response = Response(json.dumps(freights, default=dumper))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/freight', methods=['POST'])
@cross_origin()
def add_freight():
    data = request.get_json()
    db.add_freight(data)
    return "ok"

@app.route('/paths')
@cross_origin()
def get_paths():
    start = request.args.get('from')
    end = request.args.get('to')
    time = request.args.get('time')

    list_of_nodes = db.get_paths(start, end, time)
    list_of_cities = get_nodes_list(list_of_nodes)
    list_of_cases = []
    for row in list_of_cities:
        freights_list = db.get_freighs(get_node_ids(row))
        most_valuable_freights = get_most_valuable_freights(row, freights_list)
        list_of_cases.append(Case(row, most_valuable_freights))

    for case in list_of_cases:
        case.find_best_path()

    case = get_best_case(list_of_cases)
    if case is not None:
        case.print_best_path()
    response = Response(json.dumps(ReturnCase(case), default=dumper))
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.run()

