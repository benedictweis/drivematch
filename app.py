from flask import Flask, request
from flask_cors import CORS
import msgspec

from api.db import SQLiteSearchesRepository
from api.scraping import MobileDeScraper
from api.analysis import CarsAnalyzer
from api.service import DriveMatchService

# https://suchen.mobile.de/fahrzeuge/search.html?c=EstateCar&clim=AUTOMATIC_CLIMATISATION_2_ZONES&cn=DE&con=USED&dam=false&fe=CARPLAY&fe=DIGITAL_COCKPIT&fe=ELECTRIC_ADJUSTABLE_SEATS&fe=SPORT_PACKAGE&fr=2021%3A&ft=DIESEL&ft=PETROL&gn=68766%2C+Hockenheim%2C+Baden-Württemberg&isSearchRequest=true&ll=49.3261824%2C8.5186845&ml=%3A50000&od=down&p=%3A52000&pw=147%3A&rd=100&ref=srpHead&s=Car&sb=doc&tr=AUTOMATIC_GEAR&vc=Car

drive_match_service = DriveMatchService(
    SQLiteSearchesRepository("./data.db"),
    MobileDeScraper(),
    CarsAnalyzer())

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def json_response(content):
    return app.response_class(
        response=str(msgspec.json.encode(content).decode('utf-8')),
        mimetype='application/json')


@app.get("/api/v1/analyze")
def analyze():
    search_id = request.args.get('searchID', '')
    weight_hp = float(request.args.get('weightHP', ''))
    weight_price = float(request.args.get('weightPrice', ''))
    weight_mileage = float(request.args.get('weightMileage', ''))
    weight_age = float(request.args.get('weightAge', ''))
    preferred_age = float(request.args.get('preferredAge', ''))
    filter_by_manufacturer = request.args.get('filterByManufacturer', '')
    filter_by_model = request.args.get('filterByModel', '')
    result = drive_match_service.analyze(
        search_id, weight_hp, weight_price, weight_mileage, weight_age,
        preferred_age, filter_by_manufacturer, filter_by_model)
    return json_response(result)
