import { APIData } from "./types";

/**
 * Starts and displays the analysis of the search results with the url defined in the form.
 */
async function fetchAPI(url: string, weightHP: number, weightPrice: number, weightMileage: number, weightAge: number, filterByManufacturer: string, filterByModel: string): Promise<APIData> {
    const params = new URLSearchParams({
        url,
        weightHP: weightHP.toString(),
        weightPrice: weightPrice.toString(),
        weightMileage: weightMileage.toString(),
        weightAge: weightAge.toString(),
        filterByManufacturer,
        filterByModel
    });

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/analyze?${params}`);

        const data: APIData = await response.json();

        return data;
    } catch (error) {
        console.error("Error:", error);
    }
    return { scoredCars: [], groupedCars: [] };
}

export default fetchAPI;