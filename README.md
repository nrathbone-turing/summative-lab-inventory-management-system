# Inventory Management System (Flask + CLI)

## Overview
A small e-commerce admin portal with:
- Flask REST API for CRUD inventory management
- OpenFoodFacts integration
- CLI to interact with the API
- Unit tests for API, CLI, and external API integration

## Features
- Create, read, update, delete inventory items
- Lookup product details from OpenFoodFacts to prefill fields
- In-memory persistence (resets on restart); JSON file/SQLite planned
- CLI commands wire directly to the API

## Tech Stack
- **Backend:** Flask
- **HTTP:** Requests (OpenFoodFacts)
- **CLI:** Click
- **Testing:** pytest, Flask test client

## Installation & Setup

### 1. Clone & create virtual environment
```
git clone git@github.com:nrathbone-turing/summative-lab-inventory-management-system.git
cd summative-lab-inventory-management-system

python3 -m venv .venv
source .venv/bin/activate  # Mac
# .venv\Scripts\activate   # Windows
```

### 2. Install dependencies
```
pip install -r requirements.txt
pip install -e .   # install package in editable mode (for ims imports)
```

### 3. Run the API
```
# from repo root
python src/ims/server.py
# -> http://127.0.0.1:5555
```

## Data Model (current in-memory schema)
```
id               int, generated
product_name     string
barcode          string
product_quantity int
```

## Persistence
Currently, items are stored in memory only and reset on server restart.
Future versions may add:
- JSON file storage for simple persistence
- SQLite/SQLAlchemy for relational persistence

## API Endpoints
All endpoints return JSON. Invalid input returns 400, missing items return 404.
- `GET /api/items`
- `POST /api/items`
- `GET /api/items/<id>`
- `PATCH /api/items/<id>`
- `DELETE /api/items/<id>`
- `POST /api/items/<id>/restock` (body: `{"delta": <int>=0+}`)
- `POST /api/items/<id>/deduct` (body: `{"delta": <int>=0+}`)
- `GET /api/lookup/<barcode>`
- `GET /api/search?name=<q>&limit=<n>`

## Example REST Calls: create --> restock --> deduct (JSON)
```
# CREATE
curl -X POST http://127.0.0.1:5555/api/items \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Black Beans","barcode":"BEANS-400G","product_quantity":10}'
```
Response:
```
{
  "id": 1,
  "product_name": "Black Beans",
  "barcode": "BEANS-400G",
  "product_quantity": 10
}
```
```
# RESTOCK (+5)
curl -X POST http://127.0.0.1:5555/api/items/1/restock \
  -H "Content-Type: application/json" \
  -d '{"delta": 5}'
```
Response:
```
{
  "id": 1,
  "product_name": "Black Beans",
  "barcode": "BEANS-400G",
  "product_quantity": 15
}
```
```
# DEDUCT (-2)
curl -X POST http://127.0.0.1:5555/api/items/1/deduct \
  -H "Content-Type: application/json" \
  -d '{"delta": 2}'
```
Response:
```
{
  "id": 1,
  "product_name": "Black Beans",
  "barcode": "BEANS-400G",
  "product_quantity": 13
}
```
## Example CLI Usage
```
# from repo root
python -m src.ims.cli list
python -m src.ims.cli add --name "Black Beans" --barcode BEANS-400G --quantity 10
python -m src.ims.cli update 1 --quantity 20
python -m src.ims.cli delete 1
python -m src.ims.cli lookup 737628064502  # adds via OpenFoodFacts lookup
```
## Running Tests
```
pytest -v
```
Covers:
- CRUD endpoints
- Restock/deduct logic
- CLI commands
- OpenFoodFacts integration

## Project Structure
```
summative-lab-inventory-management-system/
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ .gitignore
├─ src/
│  └─ ims/
│     ├─ __init__.py
│     ├─ server.py   # Flask app + routes
│     └─ cli.py      # Click CLI
└─ tests/
   ├─ test_health.py
   ├─ test_items_crud.py
   ├─ test_items_helpers.py
   ├─ test_openfoodfacts_create.py
   ├─ test_openfoodfacts_lookup.py
   └─ test_openfoodfacts_search.py
```

## About This Repo

### Author
Nick Rathbone
[GitHub Profile](https://github.com/nrathbone-turing)

Note: This project is part of the Flatiron API Development with Python course final assessment

### License
MIT — feel free to use or remix!