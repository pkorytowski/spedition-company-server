from flask import Flask, request

from Database import Database
from Utils import get_node_ids, get_nodes_list, get_most_valuable_freights, Case, get_best_case

app = Flask(__name__)

db = Database()

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/paths')
def get_paths():
    start = request.args.get('from')
    end = request.args.get('to')

    list_of_nodes = db.get_paths(start, end)
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

    return "ok"


if __name__ == '__main__':
    app.run()

