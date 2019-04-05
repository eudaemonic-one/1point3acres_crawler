# -*- coding: utf-8 -*-
import scrapy
import re
from crawler.items import AdmissionReportItem


class AdmissionReportSpider(scrapy.Spider):
    name = 'admission_report'
    allowed_domains = ['1point3acres.com']
    start_urls = [
        ('https://www.1point3acres.com/bbs/forum.php?'
         'mod=forumdisplay&fid=82')
        ]

    def start_requests(self):
        urls = self.start_urls
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        reports = response.xpath(
            'table[@id="threadlisttableid"]/'
            'tbody[starts-with(@id,"normalthread_")]')
        for report in reports:
            detailed_report = report.xpath(
                './tr/th/a[contains(@class,"x") and contains(@class,"xst")')
            if detailed_report:
                yield scrapy.Request(
                    url=detailed_report, callback=self.parse_report)

        next_page = response.xpath(
            'span[@id="fd_page_top"]/div/a[last()]')
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_report(self, reponse):
        item = AdmissionReportItem()
        item['url'] = response.url
        # Post information
        postlist = response.xpath('div[@id="postlist"]')
        item['visit'] = postlist.xpath(
            './table[1]/tbody/tr/td[1]/div/span[2]/text()').extract()
        item['reply'] = postlist.xpath(
            './table[1]/tbody/tr/td[1]/div/span[5]/text()').extract()
        # Post topic
        item['topic'] = postlist.xpath(
            './table[1]/tbody/tr/td[2]/h1/'
            'span[@id="thread_subject"]/text()').extract()
        # User information
        item['username'] = response.xpath(
            'div[@class="auth1"]/a[@class="xi2"]/text()').extract()
        user_space_url = response.xpath(
            'div[@class="auth1"]/a[@class="xi2"]/@href').extract()
        uid_groups = re.search(r'.*?&uid=(.*?)', user_space_url)
        uid = uid_groups.group(1) if uid_groups else None
        # Summary
        summary = response.xpath('div[@class="typeoption"]/table/tbody')
        item['year'] = summary.xpath('./tr[1]/td/text()').extract()
        item['semester'] = summary.xpath('./tr[2]/td/text()').extract()
        item['major'] = summary.xpath('./tr[3]/td/text()').extract()
        item['degree'] = summary.xpath('./tr[4]/td/text()').extract()
        item['admission_type'] = summary.xpath('./tr[5]/td/text()').extract()
        item['submission_time'] = summary.xpath('./tr[6]/td/text()').extract()
        item['result'] = summary.xpath('./tr[7]/td/text()').extract()
        item['school'] = summary.xpath('./tr[8]/td/text()').extract()
        item['notification_time'] = summary.xpath(
            './tr[9]/td/text()').extract()
        item['personal_information'] = summary.xpath(
            './tr[10]/td/text()').extract()
        item['undergraduate_school_level'] = summary.xpath(
            './tr[11]/td/text()').extract()
        item['undergraduate_school'] = summary.xpath(
            './tr[12]/td/text()').extract()
        item['undergraduate_major'] = summary.xpath(
            './tr[13]/td/text()').extract()
        item['undergraduate_grade'] = summary.xpath(
            './tr[14]/td/text()').extract()
        item['graduate_school_level'] = summary.xpath(
            './tr[15]/td/text()').extract()
        item['graduate_school'] = summary.xpath('./tr[16]/td/text()').extract()
        item['graduate_major'] = summary.xpath('./tr[17]/td/text()').extract()
        item['graduate_grade'] = summary.xpath('./tr[18]/td/text()').extract()
        item['toefl_grade'] = summary.xpath('./tr[19]/td/text()').extract()
        item['gre_grade'] = summary.xpath('./tr[20]/td/text()').extract()
        item['sub_major'] = summary.xpath('./tr[21]/td/text()').extract()
        item['background'] = summary.xpath('./tr[22]/td/text()').extract()
        item['region'] = summary.xpath('./tr[23]/td/text()').extract()
        item['notification_channel'] = summary.xpath(
            './tr[24]/td/text()').extract()
        item['supplement'] = response.xpath(
            'div[@class="t_fsz"]/table/tbody/tr/'
            'td[starts-with(@id,"postmessage_")]/text()')
        return item
