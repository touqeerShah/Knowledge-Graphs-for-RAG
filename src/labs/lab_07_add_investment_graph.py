"""Lab 7: add Form 13 investment entities and relationships."""
import csv
try:
    from .common import DEFAULT_FORM13_FILE, get_graph, print_lab
except ImportError:
    from common import DEFAULT_FORM13_FILE, get_graph, print_lab

def read_form13(path=DEFAULT_FORM13_FILE) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

def run() -> None:
    print_lab(7, "Add companies, managers, and investments", """
        Knowledge graphs become more useful when different data sets are
        connected. This lab imports Form 13 rows and creates Company, Manager,
        and OWNS_STOCK_IN relationships. It then links each Company to the Form
        already created from the 10-K using the shared CUSIP identifier.
    """)
    kg = get_graph()
    rows = read_form13()
    kg.query("CREATE CONSTRAINT unique_manager IF NOT EXISTS FOR (m:Manager) REQUIRE m.managerCik IS UNIQUE")
    kg.query("""
        UNWIND $rows AS row
        MERGE (c:Company {cusip6: row.cusip6})
        SET c.companyName = row.companyName, c.cusip = row.cusip
        MERGE (m:Manager {managerCik: row.managerCik})
        SET m.managerName = row.managerName, m.managerAddress = row.managerAddress
        MERGE (m)-[owns:OWNS_STOCK_IN {reportCalendarOrQuarter: row.reportCalendarOrQuarter}]->(c)
        SET owns.value = toFloat(row.value), owns.shares = toInteger(row.shares)
    """, params={"rows": rows})
    kg.query("""
        MATCH (c:Company), (f:Form)
        WHERE c.cusip6 = f.cusip6
        MERGE (c)-[:FILED]->(f)
    """)
    print(kg.query("MATCH (:Manager)-[r:OWNS_STOCK_IN]->(:Company) RETURN count(r) AS investments"))

if __name__ == "__main__":
    run()
