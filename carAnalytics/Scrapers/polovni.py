#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy, json, re, math, codecs, pymongo, datetime, time, sys

from dbServices import updateService

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
carDB = myclient["carDB"]
polovniCollection = carDB["polovniautomobili"]


class PolovniScrap(scrapy.Spider):
    name = 'polovni_scrap'
    allowed_domains = ['polovniautomobili.com']
    start_urls = [
        'https://www.polovniautomobili.com/auto-oglasi/pretraga?page=1&sort=basic&city_distance=0&showOldNew=all&without_price=1']
    cars = []

    def parse(self, response):
        arr_urls = []
        tmpStr = response.css('div.js-hide-on-filter small::text').get()
        numE = int(re.search('Prikazano od 1 do 25 oglasa od ukupno ([0-9]*)', tmpStr).group(1))
        # print("OGLASA: " + str(numE))
        numPages = int(math.ceil(numE / 25))
        # print("BROJ STRNICA: " + str(numPages))

        for i in range(numPages):
            url = 'https://www.polovniautomobili.com/auto-oglasi/pretraga?page=' + str(
                i + 1) + '&sort=basic&city_distance=0&showOldNew=all&without_price=1'
            arr_urls.append(url)
            yield scrapy.Request(
                response.urljoin(url),
                callback=self.parse_page
            )

    def parse_page(self, response):
        carUrls = response.css(
            'article.single-classified:not([class*="uk-hidden"]):not([class*="paid-0"]) h2 a::attr(href)').getall()
        carUrls = map(lambda x: 'https://www.polovniautomobili.com' + x, carUrls)
        # print(len(carUrls))
        for url in carUrls:
            yield scrapy.Request(
                response.urljoin(url),
                callback=self.parse_car
            )

    def parse_price(self, response):
        price = response.css('div.price-item::text').get()

        if (price == '' or price == None):
            price = response.xpath('//div[has-class("price-item-discount position-relative")]').get()
            price = price.replace('\n', '').replace(' ', '').replace('\t', '')
            price = re.search(r'([0-9]*\.?[0-9]*)€', price).group(1)

        price = price.strip()
        if not (price.isdigit()) :
            price = -1
        else:
            # print(response.url)
            first = re.search('([0-9]*)\.?[0-9]*', price)
            second = re.search('[0-9]*\.([0-9]*)', price)
            if (second == None):
                price = int(first.group(1))
            else:
                price = int(first.group(1)) * 1000 + int(second.group(1))

        return price

    def parse_car(self, response):

        price = self.parse_price(response)
        exists = updateService.exists(response.url, price, "polovni")

        if exists:
            return

        sec = response.css('section.classified-content div div::text').getall()
        arr = []
        for s in sec:
            w = s.strip()
            if w != '' and '\n' not in w and '\t' not in w:
                arr.append(w)

        keys = []
        vals = []
        for i in range(len(arr)):
            if i % 2 == 0:
                keys.append(arr[i])
            else:
                vals.append(arr[i])

        x = {}

        

        for i in range(len(keys)):
            if (i < len(vals)):
                # print(keys[i])
                if (keys[i] == "Godište"):
                    since = re.search('([0-9]*).', vals[i])
                    if (since != None):
                        x["Godiste"] = int(since.group(1))
                    # else:
                        # err.write(keys[i] + ' ' + vals[i])
                elif (keys[i] == "Kubikaža"):
                    cub = re.search('([0-9]*) cm', vals[i])
                    if (cub != None):
                        x["Kubikaza"] = int(cub.group(1))
                    # else:
                    #     err.write(keys[i] + ' ' + vals[i])
                elif (keys[i] == "Kilometraža"):
                    km1 = re.search('([0-9]*)\.?[0-9]* km', vals[i])
                    km2 = re.search('[0-9]*\.([0-9]*) km', vals[i])
                    if (km1 != None):
                        if (km2 != None):
                            x["Kilometraza"] = int(km1.group(1)) * 1000 + int(km2.group(1))
                        else:
                            x["Kilometraza"] = int(km1.group(1))
                    # else:
                    #     err.write(keys[i] + ' ' + vals[i])
                    # x["Kilometraza"] = (int(re.search('([0-9]*).([0-9]*) km',vals[i]).group(1)) * (1000 if re.search('([0-9]*).([0-9]*) km',vals[i]).group(2) != '' else 1) + int(re.search('([0-9]*).([0-9]*) km',vals[i]).group(2) if re.search('([0-9]*).([0-9]*) km',vals[i]).group(2) != '' else 0) ) if vals[i] != '' else 0
                elif (keys[i] == "Snaga motora"):
                    power = re.search('([0-9]*)\/([0-9]*) \(kW\/KS\)', vals[i])
                    if (power != None):
                        x["Snaga motora"] = int(power.group(2))
                    # else:
                    #     err.write(keys[i] + ' ' + vals[i])
                else:
                    x[keys[i]] = vals[i]

        
        x['Postoji'] = True
        x['link'] = response.url
        x['logo'] = 'https://www.polovniautomobili.com/bundles/site/images/polovniautomobili-logo.svg'
        x['slika'] = response.css('ul[id="image-gallery"] li::attr(data-thumb)').get()

        price = response.css('div.price-item::text').get()

        if (price == '' or price == None):
            price = response.xpath('//div[has-class("price-item-discount position-relative")]').get()
            price = price.replace('\n', '').replace(' ', '').replace('\t', '')
            price = re.search(r'([0-9]*\.?[0-9]*)€', price).group(1)

        price = price.strip()
        if (price == "Po dogovoru"):
            price = -1
        else:
            # print(response.url)
            first = re.search('([0-9]*)\.?[0-9]*', price)
            second = re.search('[0-9]*\.([0-9]*)', price)
            if (second == None):
                price = int(first.group(1))
            else:
                price = int(first.group(1)) * 1000 + int(second.group(1))

        ts = time.gmtime()
        ts = time.strftime("%Y-%m-%d", ts)
        x['cena'] = price
        x['istorija'] = [{ts: price}]
        x['mesto'] = response.css('aside.table-cell section.uk-grid div div div.uk-width-1-2::text').get().strip()
        
        if x['mesto'] == '' :
            x['mesto'] = response.css('aside.table-cell section.uk-grid div div div div::text').get().strip()
        
        if x['mesto'] == '' :
            x['mesto'] = response.css('aside.table-cell section.uk-grid div div::text').get().strip()


        if x['mesto'] == '' :
            x['mesto'] = response.css('aside.table-cell section.uk-grid div div.uk-margin-top-remove div.uk-width-1-2::text').get().strip()
        
        
        try:
            xInsert = polovniCollection.insert_one(x)
        except Exception as e:
            err = open("err.txt", "a+")
            err.write("Unexpected error:", e)
            err.close()
        