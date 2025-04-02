from flask import Flask, request
from flask_cors import CORS
import msgspec

from api.scraping import MobileDeScraper
from api.analysis import CarsAnalyzer
from api.cache import InMemoryCachingCarsScraper, FileCachingCarsScraper

# https://suchen.mobile.de/fahrzeuge/search.html?c=EstateCar&clim=AUTOMATIC_CLIMATISATION_2_ZONES&cn=DE&con=USED&dam=false&fe=CARPLAY&fe=DIGITAL_COCKPIT&fe=ELECTRIC_ADJUSTABLE_SEATS&fe=SPORT_PACKAGE&fr=2021%3A&ft=DIESEL&ft=PETROL&gn=68766%2C+Hockenheim%2C+Baden-Württemberg&isSearchRequest=true&ll=49.3261824%2C8.5186845&ml=%3A50000&od=down&p=%3A52000&pw=147%3A&rd=100&ref=srpHead&s=Car&sb=doc&tr=AUTOMATIC_GEAR&vc=Car

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
    filterByManufacturer = request.args.get('filterByManufacturer', '')
    filterByModel = request.args.get('filterByModel', '')
    cars = carsScraper.scrape(url)
    carsAnalyzer.setCars(cars)
    scoredCars = carsAnalyzer.getScoredCars(weightHP, weightPrice, weightMileage, weightAge, filterByManufacturer, filterByModel)
    groupedCars = carsAnalyzer.getGroupedCars()
    result = {
        "scoredCars": scoredCars,
        "groupedCars": groupedCars,
    }
    return jsonResponse(result)
    