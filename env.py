import pyodbc
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-G2ETPA9;"
    "DATABASE=RestaurantIntelligenceDB;"
    "Trusted_Connection=yes;"
)
def get_db_conn():
    return pyodbc.connect(connection_string)