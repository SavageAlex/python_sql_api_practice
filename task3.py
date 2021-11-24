# Operowanie na dużych zbiorach danych staje się zdecydowanie łatwiejsze dzięki
# stronicowaniu. Dodaj tę funkcjonalność do poniższej klasy, wiedząc że API
# przyjmuje zapytania POST i PUT zawierające maksymalnie 20 obiektów i zwraca
# wyniki zapytań GET w paczkach po 40. Dokumentację znajdziesz na $DOMAIN/docs.
#
# Autoryzacja dostępu do API jest dwustopniowa:
#  1. ze ścieżki /login/aws uwierzytelnionej przez HTTP Basic Access (sekrety w
#     pliku credentials.conf.base64) uzyskasz token o określonym czasie ważności
#  2. wszystkie pozostałe ścieżki uwierzytelniane są przez podanie w nagłówku
#     Authorization ciągu "Bearer <access_token>"
#
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

    def request(self, method: str, path: str, data: dict = {}) -> dict:
        return request(
            method, f"{DOMAIN}/{path}", json=data, headers=self.headers()
        ).json()

    def get_products(self, ids: Optional[List[int]] = None) -> List[dict]:
        return self.request("GET", "products", {"ids": ids})["result"]

    def get_all_products_summary(self) -> List[dict]:
        return self.request("GET", "products", {"detailed": False})["result"]

    def get_new_products(self, newer_than: Optional[datetime] = None) -> List[dict]:
        if newer_than is None:
            newer_than = datetime.now() - timedelta(days=5)
        return self.request(
            "GET", "products", {"created_at": {"start": newer_than.isoformat()}}
        )["result"]

    def add_products(self, products: List[dict]):
        return self.request("POST", "products", {"products": products})["result"]

    def update_stocks(self, stocks: Dict[int, list]):
        current_data = self.get_products(list(stocks))
        for product_entry in current_data:
            product_entry["details"]["supply"] = stocks[product_entry["id"]]
        return self.request("PUT", "products", {"products": current_data})
