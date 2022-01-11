import datetime
from json import *
from sqlite3 import connect
from time import *
from requests import request

USE_SUPPLY_LIST = [1]
PRODUCT_LIST = [-2, -3]

for target in PRODUCT_LIST:
    print(f"target: {target}")
    try:
        sql = connect("database.sqlite")
        with sql:
            cursor = sql.cursor()
            line = str(target)
            response = request(
                "GET", f"https://recruitment.developers.emako.pl/products/example?id={line}"
            )
            product = response.json()

            if product["type"] == "product":
                print("product loaded")
                for supply in product["details"]["supply"]:
                    for stock_data in supply["stock_data"]:
                        if (stock_data['stock_id'] in USE_SUPPLY_LIST):
                            cursor.execute(
                                "INSERT INTO product_stocks "
                                "(time, product_id, variant_id, stock_id, supply) "
                                "VALUES ('{}', {}, {}, {}, {})".format(
                                    str(datetime.datetime.now())[:19],
                                    product["id"],
                                    supply["variant_id"],
                                    stock_data["stock_id"],
                                    stock_data["quantity"]
                                )
                            )
                            sql.commit()

            if product["type"] == "bundle":
                print("bundle loaded")
                bundle_products = []
                bd_pr_stock_id = 0
                for bundle_item in product["bundle_items"]:
                    bundle_products.append(bundle_item["id"])
                print(f"products in a bundle {len(bundle_products)}")
                bd_pr_supply_list = []
                for item_id in bundle_products:
                    res = request(
                        "GET",
                        f"https://recruitment.developers.emako.pl/products/example?id={item_id}"
                    )
                    bundled_product = res.json()
                    sum_supply = 0
                    for bd_supply in bundled_product["details"]["supply"]:
                        print(bd_supply)
                        for bd_stock in bd_supply["stock_data"]:
                            if (bd_stock['stock_id'] in USE_SUPPLY_LIST):
                                sum_supply += bd_stock["quantity"]
                                bd_pr_stock_id = bd_stock['stock_id']
                    bd_pr_supply_list.append(sum_supply)
                bd_pr_supply = min(bd_pr_supply_list)
                cursor.execute(
                    "INSERT INTO product_stocks "
                    "(time, product_id, variant_id, stock_id, supply) "
                    "VALUES ('{}', {}, {}, {}, {})".format(
                        str(datetime.datetime.now())[:19],
                        product["id"],
                        "NULL",
                        bd_pr_stock_id,
                        bd_pr_supply,
                    )
                )
                sql.commit
    except Exception as e:
        print(e)
    else:
        print("ok")
