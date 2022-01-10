from sqlite3 import connect

DOMAIN = "https://recruitment.developers.emako.pl"
HTTP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

sql = connect(database="database.sqlite")

# Insert your code here

from datetime import datetime
from requests.auth import HTTPBasicAuth
from requests import request
from os.path import abspath, dirname, join
from json import load, dumps



CREDENTIALS_FILE = join(dirname(abspath(__file__)), "credentials.json")
with open(CREDENTIALS_FILE, "r") as file:
    credentials = load(file)

query_param = {"grant_type": "bearer"}

response_auth = request(
    "POST",
    f"{DOMAIN}/login/aws",
    params=query_param,
    headers=HTTP_HEADERS,
    auth=HTTPBasicAuth(credentials["username"], credentials["password"]),
)

if response_auth.status_code != 200:
    print(
        f" - [ERROR] fetching access_token failed, invalid credentials? (server responded {response_auth.status_code})"
    )
    exit(2)

print(" - [OK] access_token received")

access_token = response_auth.json()["access_token"]
authorization = {"Authorization": f"Bearer {access_token}"}

AUTH_HTTP_HEADERS = {**HTTP_HEADERS, **authorization}

request_all = {
    "detailed": True,
    "pagination": {
        "page_size": 40,
        "index": 0
    }
}

response_products = request(
    'GET',
    f"{DOMAIN}/products",
    data=dumps(request_all),
    headers=AUTH_HTTP_HEADERS
    )

if response_products.status_code != 200:
    print(
        f" - [ERROR] fetching products data failed (server responded {response_auth.status_code})"
    )
    exit(2)

products = response_products.json()["result"]

print(f" - [OK] {len(products)} products data received")

id_added = []

cursor = sql.cursor()

for product in products:
    if product["type"] == "product":
        for variant_supply in product["details"]["supply"]:
            for stock_data in variant_supply["stock_data"]:
                cursor.execute(
                    "INSERT INTO product_stocks "
                    "(time, product_id, variant_id, stock_id, supply) "
                    "VALUES ('{}', {}, {}, {}, {})".format(
                        str(datetime.now())[:19],
                        product["id"],
                        variant_supply["variant_id"],
                        stock_data["stock_id"],
                        stock_data["quantity"],
                    )
                )
                id_added.append(cursor.lastrowid)
    sql.commit()


print(f" - [OK] Added {len(id_added)} records")

print(' - Start to updating records...')
id_updated = []

cursor.execute("SELECT DISTINCT product_id FROM product_stocks")
unique_db_products = cursor.fetchall()

print(f" - Found unique products id: {len(unique_db_products)}")

for unique_db_product in unique_db_products:
    print(f"   check product: {unique_db_product[0]}", end='\r')

    request_product = {
        "ids": [
            unique_db_product[0]
        ],
        "detailed": True,
        "pagination": {
            "page_size": 40,
            "index": 0
        }
    }

    response_product = request(
        'GET',
        f"{DOMAIN}/products",
        data=dumps(request_product),
        headers=AUTH_HTTP_HEADERS
        )

    product = response_product.json()["result"][0]
    if product["type"] == "product":
        for variant_supply in product["details"]["supply"]:
            for stock_data in variant_supply["stock_data"]:
                cursor.execute(
                    '''UPDATE product_stocks
                    SET time='{0}', supply={4}
                    WHERE id IN (
                        SELECT id
                        FROM product_stocks
                        WHERE product_id={1} AND variant_id={2} AND stock_id={3}
                        ORDER BY time DESC
                        LIMIT 1
                    )'''.format(
                        str(datetime.now())[:19],
                        product["id"],
                        variant_supply["variant_id"],
                        stock_data["stock_id"],
                        stock_data["quantity"],
                    )
                )
                id_updated.append(cursor.lastrowid)
    
    sql.commit()

print(f" - [OK] Updated {len(id_updated)} records")

cursor.close()

sql.close()