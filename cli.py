from typing_extensions import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from api.service import create_default_drivematch_service

app = typer.Typer()
console = Console()


drivematch_service = create_default_drivematch_service("./drivematch.db")


def search_id_matches(search_id: str):
    searches = drivematch_service.get_searches()
    for search in searches:
        if search.id.startswith(search_id):
            return search.id
    raise ValueError(f"Search with ID {search_id} not found.")               


@app.command(short_help="Displays all searches")
def searches():
    searches = drivematch_service.get_searches()
    table = Table(title="Searches")
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Name", justify="left", style="magenta")
    table.add_column("URL", justify="left", style="green")
    table.add_column("Amount of Cars", justify="center", style="blue")
    table.add_column("Date", justify="center", style="yellow")
    for search in searches:
        table.add_row(
            search.id,
            search.name,
            search.url,
            str(search.amount_of_cars),
            search.date
        )
    console.print(table)


@app.command(short_help="Scrapes a URL and saves the results under a name")
def scrape(
    name: Annotated[str, typer.Argument(help="The name of the search you are scraping")],
    url: Annotated[str, typer.Argument(help="The url of the search you are scraping")]
):
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    )
    progress.add_task(description="Scraping url...", total=None)
    progress.start()
    drivematch_service.scrape(name, url)
    progress.stop()
    console.print("Done scraping.")


@app.command(short_help="Score the results of a search with the given weights")
def scores(search_id: Annotated[str, typer.Option("--search-id", "-s", help="The ID of the search (first unique characters are enough)")],
           weight_hp: Annotated[float, typer.Option(help="Weight of the horsepower of the car", min=-10.0, max=10.0)] = 1.0,
           weight_price: Annotated[float, typer.Option(help="Weight of the price of the car", min=-10.0, max=10.0)] = -1.0,
           weight_mileage: Annotated[float, typer.Option(help="Weight of the mileage of the car", min=-10.0, max=10.0)] = -1.0,
           weight_age: Annotated[float, typer.Option(help="Weight of the age of the car", min=-10.0, max=10.0)] = -1.0,
           preferred_age: Annotated[float, typer.Option(help="Preferred age of the car", min=0.0, max=17800.0)] = 0.0,
           filter_by_manufacturer: Annotated[str, typer.Option(help="Filter inclusively by a particular manufacturer")] = "",
           filter_by_model: Annotated[str, typer.Option(help="Filter inclusively by a particular model")] = ""):
    scored_cars = drivematch_service.get_scores(
        search_id_matches(search_id),
        weight_hp,
        weight_price,
        weight_mileage,
        weight_age,
        preferred_age,
        filter_by_manufacturer,
        filter_by_model)
    scores_table = Table(title="Scored Cars")
    scores_table.add_column("Manufacturer", justify="left", style="cyan")
    scores_table.add_column("Model", justify="left", style="magenta")
    scores_table.add_column("Price", justify="center", style="blue")
    scores_table.add_column("First Registration", justify="center", style="green")
    scores_table.add_column("Horse Power", justify="center", style="red")
    scores_table.add_column("Mileage", justify="center", style="yellow")
    scores_table.add_column("Link", justify="center", style="white")
    for scored_car in scored_cars:
        scores_table.add_row(
            scored_car.car.manufacturer,
            scored_car.car.model,
            str(scored_car.car.price),
            scored_car.car.first_registration.strftime("%Y-%m-%d"),
            str(scored_car.car.horse_power),
            str(scored_car.car.mileage),
            f"[link={scored_car.car.details_url}]Link[/link]"
        )
    console.print(scores_table)


@app.command(short_help="Show the groups of cars for a search")
def groups(search_id: Annotated[str, typer.Option("--search-id", "-s", help="The ID of the search (first unique characters are enough)")]):
    grouped_cars = drivematch_service.get_groups(search_id_matches(search_id))
    groups_table = Table(title="Grouped Cars")
    groups_table.add_column("Manufacturer", justify="left", style="cyan")
    groups_table.add_column("Model", justify="left", style="magenta")
    groups_table.add_column("Count", justify="center", style="white")
    groups_table.add_column("Avg. Price", justify="center", style="blue")
    groups_table.add_column("Avg. Age", justify="center", style="green")
    groups_table.add_column("Avg. Horse Power", justify="center", style="red")
    groups_table.add_column("Avg. Mileage", justify="center", style="yellow")
    for grouped_car in grouped_cars:
        groups_table.add_row(
            grouped_car.manufacturer,
            grouped_car.model,
            str(grouped_car.count),
            f"{grouped_car.average_price:.2f}",
            f"{grouped_car.average_age:.2f}",
            f"{grouped_car.average_horse_power:.2f}",
            f"{grouped_car.average_mileage:.2f}"
        )
    console.print(groups_table)


@app.callback()
def main(db_path: Annotated[str, typer.Option("--db-path", "-d", help="The path to the drivematch database to be used")] = "./drivematch.db"):
    global drivematch_service
    drivematch_service = create_default_drivematch_service(db_path)


if __name__ == "__main__":
    app()
