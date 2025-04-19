import sqlite3

connection = sqlite3.connect("drivematch.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS searches (id TEXT PRIMARY KEY, name TEXT, url TEXT, timestamp DATETIME)")

cursor.execute("CREATE TABLE IF NOT EXISTS searches_cars (search_id TEXT, car_id TEXT, FOREIGN KEY (search_id) REFERENCES searches(id), FOREIGN KEY (car_id) REFERENCES cars(id))")

cursor.execute("CREATE TABLE IF NOT EXISTS cars (id TEXT, timestamp DATETIME, manufacturer TEXT, model TEXT, description TEXT, price INTEGER, attributes TEXT, firstRegistration DATETIME, mileage INTEGER, horsePower INTEGER, fuelType TEXT, advertisedSince DATETIME, privateSeller INTEGER, detailsURL TEXT, imageURL TEXT, PRIMARY KEY (id, timestamp))") 

connection.commit()
connection.close()
