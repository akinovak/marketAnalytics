from twisted.internet import reactor
from twisted.internet.task import deferLater
from Scrapers import polovni
from Scrapers import mojauto
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


def crash(failure):
    print('OVO U ERROR LOG SPIDER CRASHED')
    print(failure.getTraceback())


def _crawl(spider):
    deferred = process.crawl(spider)
    deferred.addErrback(crash)  # <-- add errback here
    deferred.addCallback(sleep, seconds=3600*60)
    deferred.addCallback(_crawl, spider)
    return deferred


process = CrawlerProcess(get_project_settings())

_crawl(polovni.PolovniScrap)
_crawl(mojauto.MojAutoScrap)
process.start()
