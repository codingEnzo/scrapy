#coding=utf-8

from __future__ import absolute_import

import sys
import os
import time
import json
import billiard

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../..'))

from celery import Celery
from sqlalchemy import *
from sqlalchemy.orm import *
from celerybase.task import app
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from scrapy.crawler import _get_spider_loader
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor


class Crawler_Run(billiard.Process):
    """docstring for ClassName"""
    def __init__(self, spiderName, urlList, settings):
        billiard.Process.__init__(self)
        self.celery = Celery(broker="redis://192.168.6.4/2",backend="redis://192.168.6.4/3") 
        self.crawler_runner = CrawlerRunner(settings)
        self.start_urls = urlLlist
        self.spider_loader = _get_spider_loader()
        if spiderName in spider_loader.list():
            self.spider = spider_loader.load(spider_name)
        else:
            print "There is no spider names %s"%spiderName

    def run(self):
        self.crawler_runner.crawl(self.spider,start_urls=self.start_urls)
        self.d = self.crawler_runner.join()
        self.d.addBoth(lambda _: reactor.stop())
        while reactor.running:
            self.celery.send_task("spider_service.services.spider_service.spider_call",
                        args=[self.start_urls],queue="celery_spider_queue")
            return
        reactor.run(installSignalHandlers=False)


@app.task(bind=True,default_retry_delay=60,max_retries=3)
def spider_call(self,spiderName,urlList=None,settings=None):

    settings_use = get_project_settings()
    
    if not url_list:
        print 'No url to crawl'
        return

    if settings:
        try:
            settings_dict = json.loads(settings)
            for key in settings_dict:
                settings_use[key] = settings_dict[key]
        except Exception as e:
            print Exception,":",e
    self.cur = Crawler_Run(spiderName=spiderName,urlList=urlList,settings=settings)
    try:
        self.cur.start()
        self.cur.join()
    except Exception as e:
        print Exception,":",e
        self.retry(arg=(url_list,settings_use),exc=e)
    