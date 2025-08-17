import json
from ims.server import app

def _post(client, payload):
    return client.post("/api/items", data=json.dumps(payload), content_type="application/json")

def test_items_crud_flow():
    client = app.test_client()

    # starting list (should be empty)
    resp = client.get("/api/items")
    assert resp.status_code == 200
    assert resp.get_json() == []

    # Create a new item
    payload = {"name": "Black Beans", "barcode": "BEANS-400G", "quantity": 12, "price_cents": 149}
    resp = _post(client, payload)
    assert resp.status_code == 201
    created = resp.get_json()
    assert created["id"] > 0
    assert created["name"] == "Black Beans"

    item_id = created["id"]

    # GET one item
    resp = client.get(f"/api/items/{item_id}")
    assert resp.status_code == 200
    assert resp.get_json()["barcode"] == "BEANS-400G"

    # Update (partial) with PATCH
    resp = client.patch(
        f"/api/items/{item_id}",
        data=json.dumps({"price_cents": 179}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.get_json()["price_cents"] == 179

    # DELETE one item
    resp = client.delete(f"/api/items/{item_id}")
    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": item_id}

    # GET after deleting, should return a 404
    resp = client.get(f"/api/items/{item_id}")
    assert resp.status_code == 404