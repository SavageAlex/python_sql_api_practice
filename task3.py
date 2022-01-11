from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional

from requests import request

DOMAIN = "https://recruitment.developers.emako.pl"


class Connector:
    @lru_cache
    def headers(self) -> Dict[str, str]:
        # reimplement as needed
        return {
            "Authorization": None,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_paginated_list(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def request(self, method: str, path: str, data: dict = {}) -> dict:
        return request(
            method, f"{DOMAIN}/{path}", json=data, headers=self.headers()
        ).json()

    def get_products(self, ids: Optional[List[int]] = None) -> List[dict]:
        pagination = 40
        response_list = []
        if ids:
            paginated_list = list(self.get_paginated_list(ids, pagination))
            for paginated_item in paginated_list:
                response = self.request("GET", "products", {"ids": paginated_item})["result"]
                response_list += response
        return response_list

    def pagination_g(self, req_data):
        response = self.request("GET", "products", req_data)
        response_list = response["result"]
        page_count = response["page_count"]
        if page_count != 0:
            for page in range(1, page_count):
                pagination_dict = {"pagination": {"index": page}}                
                page_response_list = self.request("GET", "products", {**req_data, **pagination_dict})["result"]
                response_list += page_response_list
        return response_list

    def get_all_products_summary(self) -> List[dict]:
        req_data = {"detailed": False}
        response_list = self.pagination_g(req_data)
        return response_list

    def get_new_products(self, newer_than: Optional[datetime] = None) -> List[dict]:
        if newer_than is None:
            newer_than = datetime.now() - timedelta(days=5)
        req_data = {"created_at": {"start": newer_than.isoformat()}}
        response_list = self.pagination_g(req_data)
        return response_list

    def pagination_p_u(self, data_list, method):
        pagination = 20
        response_list = []
        paginated_list = list(self.get_paginated_list(data_list, pagination))
        for paginated_item in paginated_list:
            response = self.request(method, "products", {"products": paginated_item})["result"]
            response_list += response
        return response_list

    def add_products(self, products: List[dict]):
        response_list = self.pagination_p_u(self, products, "POST")
        return response_list

    def update_stocks(self, stocks: Dict[int, list]):
        current_data = self.get_products(list(stocks))
        for product_entry in current_data:
            product_entry["details"]["supply"] = stocks[product_entry["id"]]
        response_list = self.pagination_p_u(self, current_data, "PUT")
        response_dict = {"result": response_list}
        return response_dict
