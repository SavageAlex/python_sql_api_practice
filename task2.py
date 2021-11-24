import datetime
import logging
import os
import pickle
import traceback
from json import *
from sqlite3 import connect
from time import *

# import boto3
# import mysql.connector as mysqlConnector
# import numpy
# import pandas as pd
# import pydantic
# import redis
import requests
from requests import request

for target in [-2, -3]:
    try:
        ok = True
        line = str(target)
        response = request(
            "GET", "https://recruitment.developers.emako.pl/products/example?id=" + line
        )
        response_content = response.content
        a = open("tmp.txt", "wb")
        a.write(response_content)
        a.flush()
        print("data downloaded from server " + str(len(response_content)))
        file = open("tmp.txt", "r")
        product = load(file)

        if product["type"] != "bundle":
            print("product loaded")
            sql = connect("database.sqlite")

            for x in product["details"]["supply"]:
                for y in x["stock_data"]:
                    if y["stock_id"] == 1:
                        productSupply = y["quantity"]
                cursor = sql.cursor()
                cursor.execute(
                    "INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES ("
                    + '"'
                    + str(datetime.datetime.now())[:19]
                    + '"'
                    + ","
                    + str(product["id"])
                    + ","
                    + str(x["variant_id"])
                    + ","
                    + str(1)
                    + ","
                    + str(productSupply)
                    + ")"
                )

        if product["type"] == "bundle":
            print("bundle loaded")
            products = []
            for p in product["bundle_items"]:
                products.append(p["id"])
            print("products " + str(len(products)))
            id = product["id"]
            all = []
            for p in products:
                r = request(
                    "GET",
                    "https://recruitment.developers.emako.pl/products/example?id="
                    + str(p),
                )
                respContent = r.content
                file = open("tmp.txt", "wb")
                file.write(respContent)
                file.flush()
                file = open("tmp.txt", "r")
                product = load(file)
                supply = 0
                for s in product["details"]["supply"]:
                    print(s)
                    for stoc in s["stock_data"]:
                        if stoc["stock_id"] == 1:
                            supply += stoc["quantity"]
                all.append(supply)
            productSupply = min(all)
            sql = connect("database.sqlite")
            cursor = sql.cursor()
            cursor.execute(
                "INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES ("
                + '"'
                + str(datetime.datetime.now())[:19]
                + '"'
                + ","
                + str(id)
                + ","
                + "NULL"
                + ","
                + str(1)
                + ","
                + str(productSupply)
                + ")"
            )
    except Exception as e:
        print(e)
        ok = False
    if ok:
        print("ok")
    else:
        print("error")
