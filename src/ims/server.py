from flask import Flask, jsonify, request

app = Flask(__name__)

# in-memory database
_DB = []
_NEXT_ID = 1

# API health check: GET /api/health

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

# CRUD: /api/items
# Internal schema
#   id                int (generated)
#   product_name      str (required)
#   barcode           str (required)
#   product_quantity  int (default = 0)

# return all items
@app.get("/api/items")
def list_items():
    return jsonify(_DB), 200

# create a new item
@app.post("/api/items")
def create_item():
    global _NEXT_ID
    data = request.get_json(silent=True) or {}

    # validation for the call, product_name and barcode required
    if "product_name" not in data or "barcode" not in data:
        return jsonify({"error": "product_name and barcode are required"}), 400

    item = {
        "id": _NEXT_ID,
        "product_name": data.get("product_name"),
        "barcode": data.get("barcode"),
        # Coerce numeric inputs; default to 0 if missing/blank
        "product_quantity": int(data.get("product_quantity", 0) or 0),
        "price_cents": int(data.get("price_cents", 0) or 0),
    }

    _NEXT_ID += 1
    _DB.append(item)
    return jsonify(item), 201

# fetch an item by id
@app.get("/api/items/<int:item_id>")
def get_item(item_id: int):
    for it in _DB:
        if it["id"] == item_id:
            return jsonify(it), 200
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# partially update an item, only for known fields and ignore any unknown key (to support clients sending extra data without breaking)
@app.patch("/api/items/<int:item_id>")
def update_item(item_id: int):
    payload = request.get_json(silent=True) or {}

    for it in _DB:
        if it["id"] == item_id:
            # only allow updates to known fields
            for key in ("product_name", "barcode", "product_quantity"):
                if key in payload:
                    # Normalize numeric types for consistency
                    if key in ("product_quantity"):
                        it[key] = int(payload[key])
                    else:
                        it[key] = payload[key]
            return jsonify(it), 200
    
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# delete item by id
@app.delete("/api/items/<int:item_id>")
def delete_item(item_id: int):
    global _DB
    before = len(_DB)
    
    _DB = [x for x in _DB if x["id"] != item_id]

    if len(_DB) < before:
        # return {deleted: <id>} if successful
        return jsonify({"deleted": item_id}), 200
    
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
