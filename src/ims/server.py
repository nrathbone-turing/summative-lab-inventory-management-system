from flask import Flask, jsonify, request

# used for OpenFoodFacts HTTP calls
import re
import requests

import urllib.parse

app = Flask(__name__)

# in-memory database

# list of item dicts
_DB = []
# auto-increment id for new items
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

    for item in _DB:
        if item["id"] == item_id:
            # only allow updates to known fields
            for key in ("product_name", "barcode", "product_quantity"):
                if key in payload:
                    # Normalize numeric types for consistency
                    if key == "product_quantity":
                        item[key] = int(payload[key])
                    else:
                        item[key] = payload[key]
            return jsonify(item), 200

    
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

# Helper routes for /restock and /deduct
# delta = how much to add or remove
# 
# delta           int (required, must be >= 0)
# deduct          int (never goes below 0 / clamp behavior)

def _parse_delta(payload):
    
    # validation that the 'delta' field is present and return the delta_int otherwise return error response or none
    
    if payload is None:
        return None, (jsonify({"error": "JSON body required"}), 400)
    if "delta" not in payload:
        return None, (jsonify({"error": "delta is required"}), 400)
    
    # Must be an integer (e.g., 5, "5" --> 5; but "abc" --> error)
    try:
        delta = int(payload["delta"])
    except (TypeError, ValueError):
        return None, (jsonify({"error": "delta must be an integer"}), 400)
    
    # Must be non-negative
    if delta < 0:
        return None, (jsonify({"error": "delta must be non-negative"}), 400)
    return delta, None

# restock route
@app.post("/api/items/<int:item_id>/restock")
def restock(item_id: int):
    """Add 'delta' to product_quantity."""
    payload = request.get_json(silent=True)
    delta, err = _parse_delta(payload)
    if err:
        return err

    for item in _DB:
        if item["id"] == item_id:
            item["product_quantity"] = int(item.get("product_quantity", 0)) + delta
            return jsonify(item), 200
    
    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# deduct route
@app.post("/api/items/<int:item_id>/deduct")
def deduct(item_id: int):
    """Subtract 'delta' from product_quantity. Never below 0 (clamp)."""
    payload = request.get_json(silent=True)
    delta, err = _parse_delta(payload)
    if err:
        return err

    for item in _DB:
        if item["id"] == item_id:
            new_qty = int(item.get("product_quantity", 0)) - delta
            # clamp at 0 so quantity is never negative
            item["product_quantity"] = new_qty if new_qty > 0 else 0
            return jsonify(item), 200

    # returns 404 if not found
    return jsonify({"error": "Not found"}), 404

# OpenFoodFacts lookup

# initial regex check to ensure the path param is digits only
_BARCODE_RE = re.compile(r"^\d+$")

def _normalize_openfoodfacts_product(openfoodfacts_payload: dict) -> dict:
    
    # convert OpenFoodFact's raw JSON into the simplified internal schema
    # and only return fields we actually need for prefill
    
    barcode = openfoodfacts_payload.get("barcode")
    product = openfoodfacts_payload.get("product") or {}
    name = product.get("product_name") or ""
    brands = product.get("brands") or ""
    brand = brands.split(",")[0].strip() if brands else None

    # preference for the numeric 'product_quantity' value if present; otherwise try to parse "quantity" i.e. like from "400 g"
    qty_raw = product.get("product_quantity")
    try:
        qty = int(qty_raw) if qty_raw is not None and str(qty_raw).strip() != "" else None
    except (TypeError, ValueError):
        qty = None

    unit = None
    if qty is None:
        # try parsing from textual quantity "400 g"
        qtext = product.get("quantity") or ""
        # regex parse logic taking the first int and first trailing word to determine unit
        m = re.match(r"\s*(\d+)\s*([A-Za-z]+)?", qtext)
        if m:
            qty = int(m.group(1))
            unit = (m.group(2) or "").lower() or None
    else:
        # if numeric qty found, try to get unit from "quantity" text using regex
        qtext = product.get("quantity") or ""
        m = re.search(r"[A-Za-z]+", qtext)
        unit = (m.group(0).lower() if m else None) or None

    return {
        "barcode": barcode,
        "product_name": name,
        "brand": brand,
        # default = 0
        "product_quantity": qty if qty is not None else 0,
        # unit is optional
        "product_quantity_unit": unit,
    }

@app.get("/api/lookup/<barcode>")
def lookup_off(barcode: str):
    
    # Lookup a product by its barcode from OpenFoodFacts and return normalized data
    if not _BARCODE_RE.match(barcode):
        # return 400 if barcode is invalid (non-digits)
        return jsonify({"error": "barcode must be digits only"}), 400

    # OpenFoodFacts v2 endpoint
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        resp = requests.get(url, headers={"User-Agent": "ims-lab/0.1"}, timeout=5)
    except Exception:
        # return 502 if the external request times out, network is down, or the domain can’t be reached
        return jsonify({"error": "upstream request failed"}), 502

    if resp.status_code != 200:
        # also return 502 if the request succeeds, but OpenFoodFacts returns something like a 404 or 500 response
        return jsonify({"error": "upstream returned non-200"}), 502

    data = resp.json()
    if not data or data.get("status") != 1:
        
        # return 404 if OpenFoodFacts says not found
        return jsonify({"error": "product not found"}), 404

    # return 200 with normalized JSON if found
    return jsonify(_normalize_openfoodfacts_product(data)), 200

def _normalize_off_product_from_list(prod: dict) -> dict:
    
    # create function to normalize a single product object from the OpenFoodFacts 'products' array in search results
    # mirrors the logic in `_normalize_openfoodfacts_product`
    
    barcode = prod.get("barcode") or prod.get("_id")
    name = (prod.get("product_name") or "").strip()
    brands = (prod.get("brands") or "").strip()
    brand = brands.split(",")[0].strip() if brands else None

    qty_raw = prod.get("product_quantity")
    try:
        qty = int(qty_raw) if qty_raw is not None and str(qty_raw).strip() != "" else None
    except (TypeError, ValueError):
        qty = None

    unit = None
    if qty is None:
        qtext = prod.get("quantity") or ""
        m = re.match(r"\s*(\d+)\s*([A-Za-z]+)?", qtext)
        if m:
            qty = int(m.group(1))
            unit = (m.group(2) or "").lower() or None
    else:
        qtext = prod.get("quantity") or ""
        m = re.search(r"[A-Za-z]+", qtext)
        unit = (m.group(0).lower() if m else None) or None

    return {
        "barcode": barcode,
        "product_name": name,
        "brand": brand,
        "product_quantity": qty if qty is not None else 0,
        "product_quantity_unit": unit,
    }

@app.get("/api/search")
def search_off_by_name():
    
    # Search products by name via OpenFoodFacts & returns a list of normalized product summaries
    # Query params:
    #   name              str (required)
    #   limit             int (optional, default = 5)
    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    limit_raw = request.args.get("limit", "5")
    try:
        limit = int(limit_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "limit must be an integer"}), 400
    if limit <= 0:
        limit = 1
    # just adding a limit for safety
    if limit > 20:
        limit = 20

    # OpenFoodFacts search (v2) and only request only the fields we need for internal schema
    fields = "code,product_name,brands,product_quantity,quantity"
    qs = urllib.parse.urlencode({
        "search_terms": name,
        "page_size": limit,
        "fields": fields,
    })
    url = f"https://world.openfoodfacts.org/api/v2/search?{qs}"

    try:
        resp = requests.get(url, headers={"User-Agent": "ims-lab/0.1"}, timeout=5)
    except Exception:
        return jsonify({"error": "upstream request failed"}), 502

    if resp.status_code != 200:
        return jsonify({"error": "upstream returned non-200"}), 502

    data = resp.json() or {}
    products = data.get("products") or []
    normalized = [_normalize_off_product_from_list(p) for p in products]
    return jsonify(normalized), 200


if __name__ == "__main__":
    app.run(debug=True)
