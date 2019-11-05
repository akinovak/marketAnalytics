import time
import pymongo
import requests
import time

try:
    import httplib
except:
    import http.client as httplib

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
carDB = myclient["carDB"]
polovniCollection = carDB["polovniautomobili"]
mojautoCollection = carDB["mojauto"]
soldCars = carDB["sold"]


# def connected_to_internet(url='http://www.google.com/', timeout=5):
#     try:
#         _ = requests.get(url, timeout=timeout)
#         return True
#     except requests.ConnectionError:
#         print("No internet connection available.")
#     return False
#
# def connected_to_polovni(url='https://www.polovniautomobili.com/', timeout=5):
#     try:
#         _ = requests.get(url, timeout=timeout)
#         return True
#     except requests.ConnectionError:
#         print("No internet connection available.")
#     return False
#
# def connected_to_mojauto(url='https://www.mojauto.rs/', timeout=5):
#     try:
#         _ = requests.get(url, timeout=timeout)
#         return True
#     except requests.ConnectionError:
#         print("No internet connection available.")
#     return False
#
# def website_available(url) :
#     if url.find("polovni") != -1:
#         connection = connected_to_polovni()
#     elif url.find("mojauto") != -1:
#         connection = connected_to_mojauto()




def _sold(document):
    ts = time.gmtime()
    ts = time.strftime("%Y-%m-%d", ts)
    document["sell_date"] = ts
    soldCars.insert_one(document)


def _loop(collection):
    for document in collection.find():
        r = requests.get(document.link)

        if r.status_code != 200:
            # Samo da odradim da li ima internet nas server i da li je aktivan sajt
            collection.delete_one(document)
            _sold(document)


mycollections = [polovniCollection, mojautoCollection]


while True:
    for collection in mycollections:
        _loop(collection)
    time.sleep(3600*5)