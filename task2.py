import datetime
import logging
import os
import pickle
import traceback
from json import *
from time import *

import boto3
import mysql.connector as mysqlConnector
import numpy
import pandas as pd
import pydantic
import redis
import requests
from requests import request

import logzero

source = open("product_list.csv")
for line in source.readlines():
    try:
        ok = True
        line = line.replace("\n", "")
        response = request("GET", "https://18.21.11.4:3900/products?id=" + line)
        response_content = reponse.content
        a = open("tmp.txt", "wb")
        a.write(response_content)
        print("data downloaded from server " + len(response_content))
        file = open("tmp.txt", "r")
        product = load(file)

        if product["type"] != "bundle":
            sql = mysqlConnector.connect(
                host="127.0.0.1", port=3306, user="admin", password="admin-pass"
            )

            for x in product["details"]["supply"]:
                for y in x["stocks_data"]:
                    if y["stock_id"] == 1:
                        productSupply = y["quantity"]
                cursor = sql.cursor()
                cursor.execute(
                    "INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES ("
                    + '"'
                    + str(datetime.datetime.now())[:19]
                    + '"'
                    + +","
                    + product["id"]
                    + ","
                    + x["variant_id"]
                    + ","
                    + str(1)
                    + ","
                    + productSupply
                    + ")"
                )

        if product["type"] == "bundle":
            products = []
            for p in product["bundle_items"]:
                products.append(p["id"])
            print("products " + len(products))
            id = product["id"]
            all = []
            for p in products:
                r = request("GET", "https://18.21.11.4:3900/products?id=" + p)
                respContent = response.content
                file = open("tmp.txt", "wb")
                file.write(respContent)
                file = open("tmp.txt", "r")
                product = load(file)
                supply = 0
                for s in product["details"]["supply"]:
                    for stoc in s["stock_data"]:
                        if stoc["stock_id"] == 1:
                            supply += stoc["quantity"]
                all.append(supply)
            productSupply = min(all)
            sql = mysqlConnector.connect(
                host="127.0.0.1", port=3306, user="admin", password="admin-pass"
            )
            cursor = sql.cursor()
            cursor.execute(
                "INSERT INTO product_stocks (time, product_id, variant_id, stock_id, supply) VALUES ("
                + '"'
                + str(datetime.datetime.now())[:19]
                + '"'
                + +","
                + id
                + ","
                + "NULL"
                + ","
                + 1
                + ","
                + productSupply
                + ")"
            )
    except Exception as e:
        ok = False
    if ok:
        print("ok")
    else:
        print("error")
