#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy, json, re, math

class MojAutoScrap(scrapy.Spider):
    name = 'mojauto_scrap'
    allowed_domains = ['mojauto.rs']
    start_urls = ['https://www.mojauto.rs/rezultat/status/automobili/vozilo_je/polovan/poredjaj-po/oglas_najnoviji/po_stranici/20/prikazi_kao/lista/stranica/1']
    cars = []

    def parse(self, response):
        arr_urls = []
        tmpStr = response.css('span.foundAdd span::text').get()
        print (tmpStr)
        numE = int(re.search('Prikazano 20 od ([0-9]*).([0-9]*)', tmpStr).group(1)) * 1000 + int(re.search('Prikazano 20 od ([0-9]*).([0-9]*)', tmpStr).group(2) if re.search('Prikazano 20 od ([0-9]*).([0-9]*)', tmpStr).group(2) != '' else 0)
        print ('OGLASA: ' + str(numE))
        numPages = int(math.ceil(numE / 20)) + 1
        print ('BROJ STRNICA: ' + str(numPages))
        for i in range(numPages):
            url = 'https://www.mojauto.rs/rezultat/status/automobili/vozilo_je/polovan/poredjaj-po/oglas_najnoviji/po_stranici/20/prikazi_kao/lista/stranica/' + str(i + 1)
            arr_urls.append(url)
            yield scrapy.Request(response.urljoin(url), callback=self.parse_page)

        print (arr_urls)
        print ('****************************************************************************************')

    def parse_page(self, response):
        carUrls = response.css('a.addTitle::attr(href)').getall()
        carUrls = map(lambda x: 'https://www.mojauto.rs' + x, carUrls)
        print ('****************************************************************************************')
        print (len(carUrls))
        for url in carUrls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_car)

    def parse_car(self, response):
        print ('****************************************************************************************')
        sec = response.css('div.breadcrumb ol li span::text').getall()
        print (sec)
        print (response.url)
        x = {}
        x['Marka'] = sec[2].encode('utf-8')
        x['Model'] = sec[3].encode('utf-8')
        price = response.css('span.priceReal::text').get()
        print (price)
        price1 = re.search('([0-9]*)\.?[0-9]*', price)
        price2 = re.search('[0-9]*\.([0-9]*)', price)
        if price1 != None:
            if price2 != None:
                x['Cena'] = int(price1.group(1))*1000 + int(price2.group(1))
            else:
                if(price1.group(1) != ''):
                    x['Cena'] = int(price1.group(1))
                else:
                    x['Cena'] = -1
        else:
            x['Cena'] = -1
        # x['Cena'] = int(re.search('([0-9]*).([0-9]*)', price).group(1)) * 1000 + int(re.search('([0-9]*).([0-9]*)', price).group(2) if re.search('([0-9]*).([0-9]*)', price).group(2) != '' else 0)
        
        optionList = response.css('div.sidePanel ul.basicSingleData li:not([class*="c_phone"]) span::text').getall()
        x['Godiste'] = int(re.search('([0-9]*).', optionList[0]).group(1))
        x['Gorivo'] = optionList[5]
        genList = response.css('div.singleBox ul:not([class*="fixed"]) li strong::text').getall()
        
        cub = re.search('([0-9]*) cm', genList[0])
        if cub != None:
            x['Kubikaza'] = int(cub.group(1))
        
        power = re.search('([0-9]*) KS', genList[1])
        if power != None:
            x['Snaga motora'] = int(power.group(1))
        
        km = re.search('([0-9]+)', genList[2])
        if km != None:
            x['Kilometraza'] = int(km.group(1))
        
        x['Karoserija'] = genList[(-1)]
        x['logo'] = 'https://www.mojauto.rs/resources/images/logo-redesign.png'
        x['link'] = response.url
        x['Postoji'] = True
        x['slika'] = 'https://www.mojauto.rs' + response.css('a[id="advertThumb_0"] img::attr(src)').get()
        print (genList)
        print (x)
        f = open('test.txt', 'a+')
        f.write(json.dumps(x) + '\n')
        f.close()
