import os

from neo4j import GraphDatabase

from Utils import Freight


class Database:
    def __init__(self):
        self.driver = GraphDatabase.driver(os.getenv("uri"), auth=(os.getenv("user"), os.getenv("password")))

    def close(self):
        self.driver.close()

    def get_paths(self, start, end):
        if start == end:
            return None
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                result = []
                for record in tx.run("match p=(n:City {name:$fr})-[r:Distance *1..10]->(m:City{name:$to}) with p, reduce (sum=0, rela in relationships(p) | sum + rela.wt) as suma where suma < $maxDist return p", fr=start, to=end, maxDist=10):
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
