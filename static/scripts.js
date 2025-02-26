"use strict";

/**
 * The APIData Object represents the data returned from the API.
 * @typedef {Object} APIData
 * @property {ScoredCar[]} scoredCars
 * @property {GroupedCarsByManufacturerAndModel[]} groupedCars
 */

/**
 * The Car Object represents a scraped Car from the website.
 * @typedef {Object} Car
 * @property {string} id
 * @property {string} manufacturer
 * @property {string} model
 * @property {string} description
 * @property {number} price
 * @property {string[]} attributes
 * @property {string} firstRegistration
 * @property {number} mileage
 * @property {number} horsePower
 * @property {string} fuelType
 * @property {string} detailsURL
 * @property {string} imageURL
 */

/**
 * The ScoredCar Object represents a car with a calculated score.
 * @typedef {Object} ScoredCar
 * @property {Car} car
 * @property {number} score
 */

/**
 * The GroupedCar Object represents a group of cars with the same manufacturer and model.
 * @typedef {Object} GroupedCarsByManufacturerAndModel
 * @property {string} manufacturer
 * @property {string} model
 * @property {number} count
 * @property {number} averagePrice
 * @property {number} averageMileage
 * @property {number} averageHorsePower
 */

/**
 * Starts and displays the analysis of the search results with the url defined in the form.
 */
async function analyzeCar() {
  showLoadingMessage();

  const params = getQueryParameters();

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/v1/analyze?${params}`);
    const data = await response.json();

    showData(data);

    hideLoadingMessage();
  } catch (error) {
    console.error("Error:", error);
    hideLoadingMessage();
  }
}

/**
 * Shows a loading message to the user.
 */
function showLoadingMessage() {
  const loadingMessage = document.getElementById("loadingMessage");
  loadingMessage.style.display = "block";
}

/**
 * Hides the loading message.
 */
function hideLoadingMessage() {
  const loadingMessage = document.getElementById("loadingMessage");
  loadingMessage.style.display = "none";
}

/**
 * Returns the query parameters from the form.
 * @returns {URLSearchParams} The query parameters.
 */
function getQueryParameters() {
  const url = document.getElementById("url").value;
  const weightHP = document.getElementById("horsepower").value;
  const weightPrice = document.getElementById("price").value;
  const weightMileage = document.getElementById("mileage").value;
  const weightAge = document.getElementById("age").value;

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
 * @param {APIData} data
 */
function showData(data) {
  showSharedCarsData(data);
  showGroupedCarsData(data);
}

/**
 * Shows the shared cars data to the user.
 * @param {APIData} data
 */
function showSharedCarsData(data) {
  const sharedCarsColumn = document.querySelector("#scoredCarsContainer");
  sharedCarsColumn.innerHTML = "";

  data.scoredCars.forEach(({ car, _ }) =>
    sharedCarsColumn.appendChild(
      createEntryWithTitleAndOptionalImage(
        ["list-entry"],
        `${car.manufacturer} ${car.model}`,
        [
          car.description,
          `${car.price}€`,
          `EZ ${new Date(car.firstRegistration).toLocaleDateString()} - ${car.mileage}km - ${car.horsePower}hp - ${car.fuelType}`,
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
 * @param {APIData} data
 */
function showGroupedCarsData(data) {
  const groupedCarsColumn = document.querySelector("#groupedCarsContainer");
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
 * @param {string[]} classList
 * @param {string} title
 * @param {string[]} paragraphs
 * @param {string} [titleLink]
 * @param {string} [imageURL]
 * @param {string} [imageAlt]
 * @returns {HTMLElement} The created scored car entry
 */
function createEntryWithTitleAndOptionalImage(classList, title, paragraphs, titleLink, imageURL, imageAlt) {
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
 * @param {HTMLElement} parent
 * @param {string} element
 * @param {string} text
 */
function appendNewElementToParentWithText(parent, element, text) {
  const newElement = document.createElement(element);
  newElement.textContent = text;
  parent.appendChild(newElement);
}
