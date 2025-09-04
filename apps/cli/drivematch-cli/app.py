import logging
import sys
from pathlib import Path
from typing import Annotated

import platformdirs
import typer
from rich.console import Console
from rich.table import Table

from drivematch.core import DriveMatchService, create_default_drivematch_service

logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()

drivematch_service: DriveMatchService
data_dir = platformdirs.user_data_dir(
    "DriveMatch",
    "DriveMatch",
    ensure_exists=True,
)
default_database_path = Path(data_dir) / "drivematch.db"


def search_id_matches(search_id: str) -> str:
    searches = drivematch_service.get_searches()
    for search in searches:
        if search.id.startswith(search_id):
            return search.id
    msg = f"Search with ID {search_id} not found."
    raise ValueError(msg)


@app.command(short_help="Displays all searches")
def searches() -> None:
    logger.info("Listing all searches")
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
            search.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        )
    console.print(table)


@app.command(short_help="Scrapes a URL and saves the results under a name")
def scrape(
    name: Annotated[
        str, typer.Argument(help="The name of the search you are scraping")
    ],
    url: Annotated[str, typer.Argument(help="The url of the search you are scraping")],
) -> None:
    logger.info("Scraping search with name %s and url %s", name, url)
    drivematch_service.scrape(name, url)


@app.command(short_help="Score the results of a search with the given weights")
def scores(  # noqa: PLR0913
    search_id: Annotated[
        str,
        typer.Option(
            "--search-id",
            "-s",
            help="The ID of the search (first unique characters are enough)",
        ),
    ],
    weight_hp: Annotated[
        float,
        typer.Option(
            "--weight-hp",
            "-h",
            help="Weight of the horsepower of the car",
            min=-10.0,
            max=10.0,
        ),
    ] = 1.0,
    weight_price: Annotated[
        float,
        typer.Option(
            "--weight-price",
            "-p",
            help="Weight of the price of the car",
            min=-10.0,
            max=10.0,
        ),
    ] = -1.0,
    weight_mileage: Annotated[
        float,
        typer.Option(
            "--weight-mileage",
            "-m",
            help="Weight of the mileage of the car",
            min=-10.0,
            max=10.0,
        ),
    ] = -1.0,
    weight_age: Annotated[
        float,
        typer.Option(
            "--weight-age",
            "-a",
            help="Weight of the age of the car",
            min=-10.0,
            max=10.0,
        ),
    ] = -1.0,
    preferred_age: Annotated[
        float, typer.Option(help="Preferred age of the car", min=0.0, max=17800.0)
    ] = 0.0,
    weight_advertisement_age: Annotated[
        float,
        typer.Option(
            help="Weight of the advertisement age of the car", min=-10.0, max=10.0
        ),
    ] = 0.0,
    preferred_advertisement_age: Annotated[
        float,
        typer.Option(
            help="Preferred advertisement age of the car", min=0.0, max=17800.0
        ),
    ] = 0.0,
    filter_by_manufacturers: Annotated[
        list[str],
        typer.Option(
            "--filter-manufacturers",
            "-m",
            help="Filter inclusively by a particular manufacturer",
        ),
    ] = [],
    filter_by_models: Annotated[
        list[str],
        typer.Option(
            "--filter-models", "-o", help="Filter inclusively by a particular model"
        ),
    ] = [],
) -> None:
    logger.info("Scoring cars for search with ID %s", search_id)
    logger.debug(
        "Using weights - HP: %s, Price: %s, Mileage: %s, Age: %s, Preferred Age: %s, Advertisement Age: %s, Preferred Advertisement Age: %s, Manufacturers: %s, Models: %s",
        weight_hp,
        weight_price,
        weight_mileage,
        weight_age,
        preferred_age,
        weight_advertisement_age,
        preferred_advertisement_age,
        filter_by_manufacturers,
        filter_by_models,
    )
    scored_cars = drivematch_service.get_scores(
        search_id_matches(search_id),
        weight_hp,
        weight_price,
        weight_mileage,
        weight_age,
        preferred_age,
        weight_advertisement_age,
        preferred_advertisement_age,
        filter_by_manufacturers,
        filter_by_models,
    )
    scores_table = Table(title=f"Scored Cars ({len(scored_cars)} cars)")
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
            f"[link={scored_car.car.details_url}]Link[/link]",
        )
    console.print(scores_table)


@app.command(short_help="Show the groups of cars for a search")
def groups(
    search_id: Annotated[
        str,
        typer.Option(
            "--search-id",
            "-s",
            help="The ID of the search (first unique characters are enough)",
        ),
    ],
) -> None:
    logger.info("Showing groups for search with ID %s", search_id)
    grouped_cars = drivematch_service.get_groups(search_id_matches(search_id))
    groups_table = Table(title=f"Grouped Cars ({len(grouped_cars)} groups)")
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
            f"{grouped_car.average_mileage:.2f}",
        )
    console.print(groups_table)


@app.callback()
def main(
    db_path: Annotated[
        str,
        typer.Option(
            "--db-path", "-d", help="The path to the drivematch database to be used"
        ),
    ] = default_database_path,
    log_level: Annotated[
        int,
        typer.Option(
            "--log-level",
            "-l",
            help=f"The log level to be used ({logging.DEBUG}, {logging.INFO}, {logging.WARNING}, {logging.ERROR}, {logging.CRITICAL})",
        ),
    ] = int(logging.WARNING),
) -> None:
    global drivematch_service  # noqa: PLW0603

    logging.basicConfig(
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        level=log_level,
    )

    logger.info("Using database at %s", db_path)

    if not Path(db_path).exists():
        logger.error("DriveMatch database not found at %s", db_path)
        sys.exit(1)

    drivematch_service = create_default_drivematch_service(db_path)


if __name__ == "__main__":
    app()
