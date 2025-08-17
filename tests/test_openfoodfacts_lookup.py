import json
from ims.server import app

def _get(client, url):
    return client.get(url)

# mock responses
class _MockResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
    def json(self):
        return self._payload

def test_expected_lookup_path(monkeypatch):
    
    #if OpenFoodFacts has the product, return normalized JSON data that matches the internal schema fields
    def fake_get(url, headers=None, timeout=5):
        # make sure barcode flowed through
        assert "3017620422003" in url
        
        return _MockResp(200, {
            "status": 1,
            "code": "3017620422003",
            "product": {
                "product_name": "Nutella",
                "brands": "Ferrero",
                "product_quantity": "400",
                "quantity": "400 g"
            }
        })

    # patch requests.get used by server
    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    client = app.test_client()
    resp = _get(client, "/api/lookup/3017620422003")
    assert resp.status_code == 200

    data = resp.get_json()
    # normalized json format expected from the API to match internal schema
    assert data["barcode"] == "3017620422003"
    assert data["product_name"] == "Nutella"
    assert data["brand"] == "Ferrero"
    assert data["product_quantity"] == 400  # coerced to int
    # unit is optional – if parsed from "quantity" field, it can be "g"
    assert data.get("product_quantity_unit") in (None, "g")


def test_lookup_not_found(monkeypatch):
 
    # if OpenFoodFacts returns status=0 (not found), the API should return 404
    def fake_get(url, headers=None, timeout=5):
        return _MockResp(200, {"status": 0, "status_verbose": "product not found", "code": "000"})
    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    client = app.test_client()
    resp = client.get("/api/lookup/000")
    assert resp.status_code == 404


def test_lookup_bad_barcode():
    # if the barcode path segment is invalid (non-digits), return 400
    client = app.test_client()
    resp = client.get("/api/lookup/abc123")
    assert resp.status_code == 400
