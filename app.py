from flask import Flask, render_template, request, make_response
import msgspec

from lib.scraping import MobileDeScraper
from lib.analysis import CarsAnalyzer
from lib.cache import InMemoryCachingCarsScraper, FileCachingCarsScraper

carsScraper = InMemoryCachingCarsScraper(FileCachingCarsScraper("./cache/", MobileDeScraper()))
carsAnalyzer = CarsAnalyzer()

app = Flask(__name__)

def jsonResponse(content):
    return app.response_class(response=str(msgspec.json.encode(content).decode('utf-8')), mimetype='application/json')

@app.get('/analyze')
def send_index():
    return render_template('index.html')

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
    