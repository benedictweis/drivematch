import { ScoredAndGroupedCars, SearchInfo } from "./types";

class DriveMatchClient {
    private apiEndpoint: string;

    constructor(apiEndpoint: string) {
        this.apiEndpoint = apiEndpoint;
    }

    public scrape(name: string, url: string): Promise<string> {
        return this.fetchAPI("scrape", new URLSearchParams({}), {
            name,
            url,
        });
    }

    public analyze(search_id: string, weight_hp: number, weight_price: number, weight_mileage: number, weight_age: number, preferred_age: number, filter_by_manufacturer: string, filter_by_model: string): Promise<ScoredAndGroupedCars> {
        return this.fetchAPI("analyze", new URLSearchParams({}), {
            search_id,
            weight_hp,
            weight_price,
            weight_mileage,
            weight_age,
            preferred_age,
            filter_by_manufacturer,
            filter_by_model,
        })
    }

    public getSearches(): Promise<SearchInfo[]> {
        return this.fetchAPI("searches", new URLSearchParams({}), {});
    }

    private async fetchAPI<T>(path: string, params: URLSearchParams, body: any): Promise<T> {
        try {
            const response = await fetch(`${this.apiEndpoint}${path}${params}`);
            const data: T = await response.json();
            return data;
        } catch (error) {
            console.error("Error:", error);
            Promise.reject("Failed to fetch api, error: " + error);
        }
        return Promise.reject("Failed to fetch api");
    }
}



export default DriveMatchClient;