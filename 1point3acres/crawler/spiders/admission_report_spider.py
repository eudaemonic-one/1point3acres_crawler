# -*- coding: utf-8 -*-
import scrapy


class AdmissionReportSpider(scrapy.Spider):
    name = 'admission_report'
    allowed_domains = ['1point3acres.com']
    start_urls = ['http://1point3acres.com/']

    def parse(self, response):
        pass
