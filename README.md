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
- Simple, reliable persistence (SQLite by default)
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
cd inventory-api

python3 -m venv .venv
source .venv/bin/activate  # Mac
# .venv\Scripts\activate   # Windows
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Environment variables
```

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

## Data Model
```

```

## API Overview

### OpenFoodFacts


## Example CLI Usage
```

```

## Project Structure
```
summative-lab-inventory-management-system/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ server.py           # main Flask app
├─ cli.py              # CLI entrypoint
├─ data.json           # simple JSON file for persistence
└─ tests/
   └─ test_app.py
```

## Persistence Flow Diagram
```

```

## About This Repo

### Author
Nick Rathbone
[GitHub Profile](https://github.com/nrathbone-turing)

Note: This project is part of the Flatiron API Development with Python course final assessment

### License
MIT — feel free to use or remix!