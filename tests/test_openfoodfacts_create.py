from ims.server import app

# mocked response data
class _MockResp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
    def json(self): 
        return self._payload

def test_create_from_lookup(monkeypatch):
    def fake_get(url, headers=None, timeout=5):
        return _MockResp(200, {
            "product": {
                "barcode": "12345",
                "product_name": "Mock Item",
                "brands": "BrandX",
                "quantity": "10 g",
                "product_quantity": 10,
            }
        })

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    client = app.test_client()
    resp = client.post("/api/items/from_lookup?barcode=12345")
    
    assert resp.status_code == 201

    data = resp.get_json()
    print("DEBUG:", data)

    assert data["barcode"] == "12345"
    assert data["product_name"] == "Mock Item"
    assert data["brand"] == "BrandX"