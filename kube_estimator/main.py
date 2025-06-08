# kube_estimator/main.py
import yaml
from typing_extensions import Annotated
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

# For now, we hardcode the price. This is a key MVP decision.
# AWS EBS gp3 storage in us-east-1 is $0.08 per GB-month.
AWS_EBS_GP3_PRICE_PER_GB_MONTH = 0.08

app = typer.Typer()
console = Console()


def parse_storage_size(size: str) -> float:
    """Converts Kubernetes storage size (e.g., 10Gi, 500Mi) to GB."""
    size = size.lower()
    if size.endswith("gi"):
        return float(size.replace("gi", ""))
    elif size.endswith("mi"):
        return float(size.replace("mi", "")) / 1024
    elif size.endswith("ki"):
        return float(size.replace("ki", "")) / (1024 * 1024)
    return 0.0


@app.command()
def estimate(
    filepath: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to the Kubernetes YAML file to estimate.",
        ),
    ],
):
    """
    Estimates the monthly cost of PersistentVolumeClaims in a K8s manifest.
    """
    console.print(f"📄 Analyzing file: [bold cyan]{filepath.name}[/bold cyan]")

    total_cost = 0.0
    pvc_found = False

    table = Table(
        title="Kube-Estimator Cost Report (AWS us-east-1, gp3)",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Kind", style="dim")
    table.add_column("Name")
    table.add_column("Storage Request")
    table.add_column("Estimated Monthly Cost", justify="right")

    try:
        with open(filepath, "r") as f:
            docs = yaml.safe_load_all(f)
            for doc in docs:
                if doc and doc.get("kind") == "PersistentVolumeClaim":
                    pvc_found = True
                    name = doc["metadata"]["name"]
                    storage_req = doc["spec"]["resources"]["requests"]["storage"]
                    storage_gb = parse_storage_size(storage_req)
                    cost = storage_gb * AWS_EBS_GP3_PRICE_PER_GB_MONTH
                    total_cost += cost
                    table.add_row(
                        "PersistentVolumeClaim",
                        name,
                        storage_req,
                        f"${cost:.2f}",
                    )

    except Exception as e:
        console.print(f"❌ [bold red]Error processing file:[/] {e}")
        raise typer.Exit(code=1)

    if not pvc_found:
        console.print(
            "No 'PersistentVolumeClaim' resources found in the file.",
            style="yellow",
        )
        raise typer.Exit()

    console.print(table)
    console.print(
        f"\n[bold]Total Estimated Monthly Cost: [green]${total_cost:.2f}[/green][/bold]"
    )


if __name__ == "__main__":
    app()