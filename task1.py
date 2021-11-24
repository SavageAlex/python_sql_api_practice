from sqlite3 import connect

DOMAIN = "https://recruitment.developers.emako.pl"
HTTP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

sql = connect(database="database.sqlite")

# Insert your code here

sql.close()
