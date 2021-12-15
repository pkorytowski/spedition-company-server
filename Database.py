import os

from neo4j import GraphDatabase

from Utils import Freight, City, Relationship, CityWithRelationship, FreightForGetAll


class Database:
    def __init__(self):
        self.driver = GraphDatabase.driver(os.getenv("uri"), auth=(os.getenv("user"), os.getenv("password")))

    def close(self):
        self.driver.close()

    def get_paths(self, start, end, time):
        if start == end:
            return None
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = []
                for record in tx.run("match p=(n:City {name:$fr})-[r:Distance *1..10]->(m:City{name:$to}) with p, reduce (sum=0, rela in relationships(p) | sum + rela.wt) as suma where suma < $maxDist return p", fr=start, to=end, maxDist=float(time)):
                    row = list(record["p"].nodes)
                    result.append(row)
                return result

    def get_freighs(self, list_of_nodes):
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                list_of_freights = []
                for record in tx.run("match (m:Freight)-[r:From]->(n:City) match (m)-[s:To]-(o:City) where ID(n) in $nodes and ID(o) in $nodes return m, r, s", nodes=list_of_nodes):
                    list_of_freights.append(Freight(record["m"], record["r"], record["s"]))
                return list_of_freights

    def get_all_freights(self):
        freights = []
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for record in tx.run("match (m:Freight)-[r:From]->(n:City) match (m)-[s:To]-(o:City) return m, r, n, s, o"):
                    freights.append(FreightForGetAll(Freight(record["m"], record["r"], record["s"]), City(record["n"]), City(record["o"])))
        return freights

    def add_freight(self, data):
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result1 = tx.run("create (n:Freight{name:$name, value:$value}) return ID(n)", name=data['name'], value=data['value'])
                id = result1.single().value()
                tx.run("match (m:Freight), (n:City) where ID(m)=$id and n.name=$name create (m)-[:From]->(n) return m", id=id, name=data['from'])
                tx.run("match (m:Freight), (n:City) where ID(m)=$id and n.name=$name create (m)-[:To]->(n) return m", id=id, name=data['to'])

    def get_all_cities(self):
        cities = []
        ids = {}
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for record in tx.run("match (n:City)-[r:Distance]-(m:City) return n, r, m"):
                    city = CityWithRelationship(City(record["n"]))
                    if city.city.id in ids.keys():
                        r = Relationship(record["r"], City(record["m"]))
                        city2 = cities[ids[city.city.id]]
                        if r.city.name not in city2.get_relationships_names():
                            city2.relationships.append(r)
                    else:
                        city.relationships.append(Relationship(record["r"], City(record["m"])))
                        cities.append(city)
                        ids[city.city.id] = len(cities)-1
        return cities


