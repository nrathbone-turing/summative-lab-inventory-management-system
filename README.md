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
- Simple, reliable persistence (JSON file for now, SQLite later)
- CLI commands wire directly to the API

## Tech Stack
- **Backend:** Flask
- **HTTP:** Requests (for OpenFoodFacts)
- **CLI:** Argparse
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

### 3. Environment variables
Create a `.env` file in the project root:
```
FLASK_APP=ims.server
FLASK_RUN_PORT=5555
FLASK_ENV=development
```

### 4. Initialize database (first run)
```
python -m server.manage db-init     
python -m server.manage db-seed     # sample data
```

### 5. Run the API
```
flask run
# => http://127.0.0.1:5000
```

## Progress Checklist (based on rubric)

### Flask Routing
- [X] At least 1 route built with Flask (GET /api/health)
- [X] CRUD routes for `/items`
- [X] Additional helper routes (e.g., /items/<id>/restock, /items/<id>/deduct)

### CRUD
- [X] Create (POST /items)
- [X] Read (GET /items and GET /items/<id>)
- [X] Update (PATCH /items/<id>)
- [X] Delete (DELETE /items/<id>)

### External API Integration
- [ ] Build route to fetch data from OpenFoodFacts (GET /lookup?barcode=...)
- [ ] Build route to search products by name (GET /search?name=...)
- [ ] Add fetched data into local database/array

### Git Management
- [X] Use git regularly for commits
- [X] Create feature branches for routes, CLI, external API, etc.
- [X] Open pull requests and merge into main
- [X] Clear branches after merge

### Testing
- [X] Test health route
- [X] Test CRUD operations
- [ ] Test external API integration (mock requests)
- [ ] Full test suite covering features

## Data Model
```
(id)       int, primary key
name       string
sku        string
barcode    string
brand      string
category   string
unit       string
quantity   int
price_cents int
created_at datetime
updated_at datetime
```

## API Overview

(Coming soon)


## Example CLI Usage
```
python -m ims.cli --help
python -m ims.cli items list
python -m ims.cli items add --name "Black Beans" --quantity 12
```

## Project Structure
```
summative-lab-inventory-management-system/
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ .gitignore
├─ .env
├─ src/
│  └─ ims/
│     ├─ __init__.py
│     ├─ server.py      # Flask app
│     └─ cli.py         # CLI entry
└─ tests/
   └─ test_app.py
```

## Persistence Flow Diagram

(Coming soon)

## About This Repo

### Author
Nick Rathbone
[GitHub Profile](https://github.com/nrathbone-turing)

Note: This project is part of the Flatiron API Development with Python course final assessment

### License
MIT — feel free to use or remix!