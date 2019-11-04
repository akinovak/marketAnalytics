import time
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
carDB = myclient["carDB"]
polovniCollection = carDB["polovniautomobili"]
mojautoCollection = carDB["mojauto"]


def exists(link, price, website):
    if website == "polovni":
        return update(link, price, polovniCollection)
    elif website == "mojauto":
        return update(link, price, mojautoCollection)


def update(link, price, collection):
    car = collection.find_one({"link": link}, {"cena": 1, "istorija": 1})
    if car:
        ts = time.gmtime()
        ts = time.strftime("%Y-%m-%d", ts)
        car['cena'] = price
        car['istorija'].append({ts: price})
        collection.update_one({'_id': car['_id']}, {"$set": {'cena': price, 'istorija': car['istorija']}})
        return True
    else:
        return False
