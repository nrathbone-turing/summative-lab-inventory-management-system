import json
from ims.server import app

def _post_json(client, url, body):
    # helper so I don't have to repeat content_type everywhere
    return client.post(url, data=json.dumps(body), content_type="application/json")

def _create_item(client, name="Test Beans", barcode="TEST-123", qty=10):
    
    # CREATE one new item to use for restock/deduct tests
    # returns the created item JSON.
    
    payload = {"product_name": name, "barcode": barcode, "product_quantity": qty}
    resp = _post_json(client, "/api/items", payload)
    assert resp.status_code == 201
    return resp.get_json()


def test_restock_basic():
    
    # starts with quantity 10
    # restock 5 --> new quantity should be 15
    
    client = app.test_client()
    item = _create_item(client, qty=10)

    resp = _post_json(client, f"/api/items/{item['id']}/restock", {"delta": 5})
    assert resp.status_code == 200
    assert resp.get_json()["product_quantity"] == 15


def test_deduct_basic():
    
    # starts with quantity 10
    # deducts 4 --> new quantity should be 6
    # deduct 999 --> new quantity clamps to 0 (never negative)
    
    client = app.test_client()
    item = _create_item(client, qty=10)
    item_id = item["id"]

    # deduct 4 --> 6
    resp = _post_json(client, f"/api/items/{item_id}/deduct", {"delta": 4})
    assert resp.status_code == 200
    assert resp.get_json()["product_quantity"] == 6

    # if you try to deduct more than you have, it just goes to 0 (clamped)
    resp = _post_json(client, f"/api/items/{item_id}/deduct", {"delta": 999})
    assert resp.status_code == 200
    assert resp.get_json()["product_quantity"] == 0


def test_validation_simple_errors():
    """
    Simple validation checks:
    - Missing delta --> returns a 400
    - Negative delta -> returns a 400
    - Non-integer delta -> returns a 400
    """
    client = app.test_client()
    item = _create_item(client, qty=10)

    # Missing delta
    resp = _post_json(client, f"/api/items/{item['id']}/restock", {})
    assert resp.status_code == 400

    # Negative delta
    resp = _post_json(client, f"/api/items/{item['id']}/restock", {"delta": -1})
    assert resp.status_code == 400

    # Non-integer delta
    resp = _post_json(client, f"/api/items/{item['id']}/restock", {"delta": "abc"})
    assert resp.status_code == 400