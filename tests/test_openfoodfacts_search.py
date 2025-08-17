import json
from ims.server import app

def _get(client, url):
    return client.get(url)

# mock response object
class _MockResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
    def json(self):
        return self._payload

def test_search_expected_path(monkeypatch):
    
    # if OpenFoodFacts successfully returns products from a name query, then return a list of normalized items (barcode, product_name, brand, qty, unit)
    def fake_get(url, headers=None, timeout=5):
        assert "choco" in url.lower()
        # example OpenFoodFacts-like payload
        return _MockResp(200, {
            "count": 2,
            "products": [
                {
                    "code": "111",
                    "product_name": "Choco Spread",
                    "brands": "BrandA",
                    "product_quantity": "400",
                    "quantity": "400 g",
                },
                {
                    "code": "222",
                    "product_name": "Choco Bar",
                    "brands": "BrandB, Other",
                    "quantity": "50 g",
                },
            ],
        })

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    client = app.test_client()
    resp = _get(client, "/api/search?name=choco&limit=2")
    assert resp.status_code == 200

    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2

    first = data[0]
    assert first["barcode"] == "111"
    assert first["product_name"] == "Choco Spread"
    assert first["brand"] == "BrandA"
    assert first["product_quantity"] == 400
    assert first.get("product_quantity_unit") in (None, "g")

    second = data[1]
    assert second["barcode"] == "222"
    assert second["product_name"] == "Choco Bar"
    assert second["brand"] == "BrandB"

def test_search_requires_name():
    client = app.test_client()
    resp = client.get("/api/search")
    assert resp.status_code == 400

def test_search_limit_validation(monkeypatch):
    
    # expected that a non-integer limit should be rejected with a 400 code
    def fake_get(url, headers=None, timeout=5):
        return _MockResp(200, {"count": 0, "products": []})

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    client = app.test_client()
    resp = client.get("/api/search?name=beans&limit=abc")
    assert resp.status_code == 400
