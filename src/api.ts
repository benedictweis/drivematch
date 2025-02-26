/**
 * Starts and displays the analysis of the search results with the url defined in the form.
 */
async function analyzeCar(): Promise<void> {
    console.log("hi");

    const params = getQueryParameters();

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/analyze?${params}`);

        const data: APIData = await response.json();

        showData(data);
    } catch (error) {
        console.error("Error:", error);
    }
}

/**
 * Returns the query parameters from the form.
 */
function getQueryParameters(): URLSearchParams {
    const url = (document.getElementById("url") as HTMLInputElement).value;
    const weightHP = (document.getElementById("horsepower") as HTMLInputElement).value;
    const weightPrice = (document.getElementById("price") as HTMLInputElement).value;
    const weightMileage = (document.getElementById("mileage") as HTMLInputElement).value;
    const weightAge = (document.getElementById("age") as HTMLInputElement).value;

    return new URLSearchParams({
        url,
        weightHP: weightHP,
        weightPrice: weightPrice,
        weightMileage: weightMileage,
        weightAge: weightAge,
    });
}

/**
 * Shows the data to the user.
 */
function showData(data: APIData): void {
    showSharedCarsData(data);
    showGroupedCarsData(data);
}

/**
 * Shows the shared cars data to the user.
 */
function showSharedCarsData(data: APIData): void {
    const sharedCarsColumn = document.querySelector("#scoredCarsContainer") as HTMLElement;
    sharedCarsColumn.innerHTML = "";

    data.scoredCars.forEach(({ car }) =>
        sharedCarsColumn.appendChild(
            createEntryWithTitleAndOptionalImage(
                ["list-entry"],
                `${car.manufacturer} ${car.model}`,
                [
                    car.description,
                    `${car.price}€`,
                    `EZ ${new Date(car.firstRegistration).toLocaleDateString()}-${car.mileage}km-${car.horsePower}hp-${car.fuelType}`,
                ],
                car.detailsURL,
                car.imageURL,
                `${car.manufacturer} ${car.model}`,
            ),
        ),
    );
}

/**
 * Shows the grouped cars data to the user.
 */
function showGroupedCarsData(data: APIData): void {
    const groupedCarsColumn = document.querySelector("#groupedCarsContainer") as HTMLElement;
    groupedCarsColumn.innerHTML = "";

    data.groupedCars.forEach((group) =>
        groupedCarsColumn.appendChild(
            createEntryWithTitleAndOptionalImage(["list-entry"], `${group.manufacturer} ${group.model}`, [
                `Count: ${group.count}`,
                `Average Price: ${group.averagePrice.toFixed(2)}€`,
                `Average Mileage: ${group.averageMileage.toFixed(2)}km`,
                `Average Horsepower: ${group.averageHorsePower.toFixed(2)}hp`,
            ]),
        ),
    );
}

/**
 * Creates a new list entry with a title, paragraphs, and optional image for scored cars.
 */
function createEntryWithTitleAndOptionalImage(
    classList: string[],
    title: string,
    paragraphs: string[],
    titleLink?: string,
    imageURL?: string,
    imageAlt?: string,
): HTMLElement {
    const entry = document.createElement("div");
    entry.classList.add(...classList);

    if (imageURL) {
        const image = document.createElement("img");
        image.classList.add("car-image");
        image.src = imageURL;
        if (imageAlt) {
            image.alt = imageAlt;
        }
        entry.appendChild(image);
    }

    const titleElement = document.createElement("h3");
    if (titleLink) {
        const link = document.createElement("a");
        link.href = titleLink;
        link.textContent = title;
        titleElement.appendChild(link);
    } else {
        titleElement.textContent = title;
    }
    entry.appendChild(titleElement);

    paragraphs.forEach((text) => appendNewElementToParentWithText(entry, "p", text));

    return entry;
}

/**
 * Helper function to create a new HTMLElement with text and append it to a parent.
 */
function appendNewElementToParentWithText(parent: HTMLElement, element: string, text: string): void {
    const newElement = document.createElement(element);
    newElement.textContent = text;
    parent.appendChild(newElement);
}

export default analyzeCar;