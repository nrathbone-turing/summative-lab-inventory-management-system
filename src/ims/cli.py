import click
import requests

API_URL = "http://127.0.0.1:5555/api/items"

@click.group()
def cli():
    # Inventory CLI for interacting with the API
    pass

# View inventory
@cli.command("list")
def list_items():
    # List all inventory items
    try:
        resp = requests.get(API_URL, timeout=5)
        resp.raise_for_status()
        items = resp.json()
        if not items:
            click.echo("No items found.")
        for item in items:
            click.echo(f"{item['id']}: {item['product_name']} (qty={item['product_quantity']})")
    except Exception as e:
        click.echo(f"Error: {e}")

# Add new item manually
@cli.command("add")
@click.option("--name", prompt=True, help="Product name")
@click.option("--barcode", prompt=True, help="Barcode")
@click.option("--quantity", default=1, help="Quantity")
def add_item(name, barcode, quantity):
    # Add a new item manually    
    payload = {"product_name": name, "barcode": barcode, "product_quantity": quantity}

    try:
        resp = requests.post(API_URL, json=payload, timeout=5)
        resp.raise_for_status()
        click.echo(f"Added item: {resp.json()}")
    except Exception as e:
        click.echo(f"Error: {e}")

# Add item via lookup (external API)
@cli.command("lookup")
@click.argument("barcode")
def lookup_item(barcode):
    # Fetch item from external API and add it locally
    try:
        resp = requests.post(f"{API_URL}/from_lookup?barcode={barcode}", timeout=5)
        if resp.status_code == 201:
            click.echo(f"Added item: {resp.json()}")
        else:
            click.echo(f"Lookup failed: {resp.status_code} {resp.text}")
    except Exception as e:
        click.echo(f"Error: {e}")

# Update item
@cli.command("update")
@click.argument("item_id")
@click.option("--quantity", type=int, help="New quantity")
def update_item(item_id, quantity):
    # Update quantity of an item by id
    payload = {}
    if quantity is not None:
        payload["product_quantity"] = quantity 

    try:
        resp = requests.patch(f"{API_URL}/{item_id}", json=payload, timeout=5)
        if resp.ok:
            click.echo(f"Updated item: {resp.json()}")
        else:
            click.echo(f"Update failed: {resp.status_code} {resp.text}")
    except Exception as e:
        click.echo(f"Error: {e}")

# Delete item
@cli.command("delete")
@click.argument("item_id")
def delete_item(item_id):
    # Delete an item by id
    try:
        resp = requests.delete(f"{API_URL}/{item_id}", timeout=5)
        if resp.status_code == 200:
            click.echo("Item deleted.")
        else:
            click.echo(f"Delete failed: {resp.status_code} {resp.text}")
    except Exception as e:
        click.echo(f"Error: {e}")

if __name__ == "__main__":
    cli()