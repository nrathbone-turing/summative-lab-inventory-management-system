import click

@click.group()
def cli():
    """Inventory CLI (stub)."""
    pass

@cli.command()
def list_items():
    """Stub for listing items."""
    click.echo("TODO: call GET /api/items")

if __name__ == "__main__":
    cli()
