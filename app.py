from flask import Flask, request
from flask_cors import CORS, cross_origin
import msgspec

from svc.scraping import MobileDeScraper
from svc.analysis import CarsAnalyzer
from svc.cache import InMemoryCachingCarsScraper, FileCachingCarsScraper

carsScraper = InMemoryCachingCarsScraper(FileCachingCarsScraper("./cache/", MobileDeScraper()))
carsAnalyzer = CarsAnalyzer()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def jsonResponse(content):
    return app.response_class(response=str(msgspec.json.encode(content).decode('utf-8')), mimetype='application/json')

@app.get("/api/v1/analyze")
def hello_world():
    url = request.args.get('url', '')
    weightHP = float(request.args.get('weightHP', ''))
    weightPrice = float(request.args.get('weightPrice', ''))
    weightMileage = float(request.args.get('weightMileage', ''))
    weightAge = float(request.args.get('weightAge', ''))
    cars = carsScraper.scrape(url)
    carsAnalyzer.setCars(cars)
    scoredCars = carsAnalyzer.getScoredCars(weightHP, weightPrice, weightMileage, weightAge)
    groupedCars = carsAnalyzer.getGroupedCars()
    result = {
        "scoredCars": scoredCars,
        "groupedCars": groupedCars,
    }
    return jsonResponse(result)
    