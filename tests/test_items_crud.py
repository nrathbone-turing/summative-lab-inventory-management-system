import json
from ims.server import app

def _post(client, payload):
    return client.post(
        "/api/items",
        data=json.dumps(payload),
        content_type="application/json",
    )

def test_items_crud_flow():
    client = app.test_client()

    # List (should start empty)
    resp = client.get("/api/items")
    
    assert resp.status_code == 200
    assert resp.get_json() == []

    # CREATE a new item
    payload = {
        "product_name": "Black Beans",
        "barcode": "BEANS-400G",
        "product_quantity": 12,
    }
    
    resp = _post(client, payload)
    
    assert resp.status_code == 201
    
    created = resp.get_json()
    
    assert created["id"] > 0
    assert created["product_name"] == "Black Beans"
    assert created["barcode"] == "BEANS-400G"
    assert created["product_quantity"] == 12

    item_id = created["id"]

    # READ one item
    resp = client.get(f"/api/items/{item_id}")
    
    assert resp.status_code == 200
    assert resp.get_json()["barcode"] == "BEANS-400G"

    # UPDATE (partial with PATCH)
    resp = client.patch(
        f"/api/items/{item_id}",
        data=json.dumps({"product_quantity": 18}),
        content_type="application/json",
    )
    
    assert resp.status_code == 200
    assert resp.get_json()["product_quantity"] == 18

    # DELETE one item
    resp = client.delete(f"/api/items/{item_id}")
    
    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": item_id}

    # READ after deleting, should return a 404
    resp = client.get(f"/api/items/{item_id}")
    
    assert resp.status_code == 404