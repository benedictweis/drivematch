/**
 * The ScoredAndGroupedCars Object represents the data returned from the API.
 */
interface ScoredAndGroupedCars {
    scoredCars: ScoredCar[];
    groupedCars: GroupedCarsByManufacturerAndModel[];
}

/**
 * The Car Object represents a scraped Car from the website.
 */
interface Car {
    id: string;
    manufacturer: string;
    model: string;
    description: string;
    price: number;
    attributes: string[];
    firstRegistration: string;
    mileage: number;
    horsePower: number;
    fuelType: string;
    detailsURL: string;
    imageURL: string;
}

/**
 * The ScoredCar Object represents a car with a calculated score.
 */
interface ScoredCar {
    car: Car;
    score: number;
}

/**
 * The GroupedCar Object represents a group of cars with the same manufacturer and model.
 */
interface GroupedCarsByManufacturerAndModel {
    manufacturer: string;
    model: string;
    count: number;
    averagePrice: number;
    averageMileage: number;
    averageHorsePower: number;
    averageAge: number;
}

interface SearchInfo {
    id: string
    name: string
    url: string
    amount_of_cars: number
    date: string
}

export type { ScoredAndGroupedCars, Car, ScoredCar, GroupedCarsByManufacturerAndModel, SearchInfo };