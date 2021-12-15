def get_node_names(nodes):
    result = []
    for row in nodes:
        result_row = []
        for node in row:
            result_row.append(node.name)
        result.append(result_row)
    return result


def get_node_ids(nodes):
    result = []
    for node in nodes:
        result.append(node.id)
    return result


def get_most_valuable_freights(nodes, freights):
    result = []
    for start_node in nodes:
        for end_node in nodes:
            value = 0
            node = None
            for freight in freights:
                if freight.get_from_id() == start_node.id and freight.get_to_id() == end_node.id:

                    if freight.get_value() > value:
                        node = freight
                        value = freight.get_value()
            if node is not None:
                result.append(node)
    return result


def get_nodes_list(query_result):
    result = []
    for row in query_result:
        nodes = []
        for item in row:
            nodes.append(City(item))
        result.append(nodes)
    return result


def get_best_case(list_of_cases):
    if not list_of_cases:
        return None
    value = 0
    idx = 0
    for i, case in enumerate(list_of_cases):
        if case.get_best_path_value() > value:
            value = case.get_best_path_value()
            idx = i
    return list_of_cases[idx]


class City:
    def __init__(self, node):
        self.id = node._id
        self.name = node._properties["name"]


class CityWithRelationship:
    def __init__(self, city):
        self.city = city
        self.relationships = []

    def get_relationships_names(self):
        return [rel.city.name for rel in self.relationships]


class Relationship:
    def __init__(self, relationship, city):
        self.distance = relationship._properties["wt"]
        self.city = city


class FreightForGetAll:
    def __init__(self, freight, start, end):
        self.name = freight.get_name()
        self.value = freight.get_value()
        self.start = start
        self.end = end


class Freight:
    def __init__(self, freight, begin, end):
        self.freight = freight
        self.begin = begin
        self.end = end

    def get_from_id(self):
        return self.begin.end_node._id

    def get_to_id(self):
        return self.end.end_node._id

    def get_value(self):
        return float(self.freight._properties['value'])

    def get_name(self):
        return self.freight._properties['name']


class Case:
    def __init__(self, nodes, freights):
        self.cities = nodes
        self.freights = freights
        self.nodes_map = {item.id: i for i, item in enumerate(self.cities)}
        self.length = len(self.cities)
        self.best_path = None

    def get_best_path_value(self):
        val = 0
        if self.best_path is not None:
            for item in self.best_path:
                val = val + item.get_value()
        return val

    def find_best_path(self):
        freights_arr = [[None for col in range(self.length)] for row in range(self.length)]
        values_arr = [[0 for col in range(self.length)] for row in range(self.length)]

        for freight in self.freights:
            freights_arr[self.nodes_map[freight.get_from_id()]][self.nodes_map[freight.get_to_id()]] = freight

        for i in range(self.length):
            if freights_arr[0][i] is not None:
                values_arr[0][i] = freights_arr[0][i].get_value()

        for i in range(1, self.length-1):
            for j in range(i, self.length):
                if i==j:
                    values_arr[i][j] = values_arr[i-1][j]
                else:
                    if freights_arr[i][j] is not None:
                        values_arr[i][j] = values_arr[i][i] + freights_arr[i][j].get_value()
                    else:
                        values_arr[i][j] = values_arr[i][i]
        col = self.length-1
        steps = []
        while col > 0:
            max = 0
            idx = col
            for row in range(col):
                if values_arr[row][col] > max:
                    idx = row
                    max = values_arr[row][col]
            if col != idx:
                steps.append((idx, col))
                col = idx
            else:
                col = 0
        list_of_steps = list(reversed(steps))
        freights_list = []
        for (i, j) in list_of_steps:
            if freights_arr[i][j] is not None:
                freights_list.append(freights_arr[i][j])

        self.best_path = freights_list

    def print_best_path(self):
        if self.best_path is not None:
            for item in self.best_path:
                print('Product: ', item.get_name(), " From: ", self.cities[self.nodes_map[item.get_from_id()]].name, " To: ", self.cities[self.nodes_map[item.get_to_id()]].name, " Value: ", item.get_value())
            print("Total value: ", self.get_best_path_value())


class ReturnCase:
    def __init__(self, case):
        self.nodes = [city.name for city in case.cities]
        self.freights = [FreightForGetAll(item, case.cities[case.nodes_map[item.get_from_id()]].name, case.cities[case.nodes_map[item.get_to_id()]].name) for item in case.best_path]
        self.value = case.get_best_path_value()


def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

