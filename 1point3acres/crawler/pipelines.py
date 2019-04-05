# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
import pymongo


class AdmissionReportPipeline(object):
    def __init__(self):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.ids_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Drop duplicates
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['topic'])

        # Write items to MongoDB
        collection = self.db[self.collection_name]
        collection.update_one(
            {'topic': item['topic']}, {'$set': item}, upsert=True
        )
        return item
