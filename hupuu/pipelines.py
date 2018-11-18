# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook
from scrapy.conf import settings
import pymongo
from datetime import datetime






class HupuuPipeline(object):
  
    def __init__(self):
        host=settings['MONGODB_HOST']
        port=settings['MONGODB_PORT']
        dbname=settings['MONGODB_DBNAME']#数据库名
        client=pymongo.MongoClient(host=host,port=port)
        self.tdb=client[dbname]
        
    def process_item(self, item, spider):
        agentinfo=dict(item)
        self.port=self.tdb[item.tablename]#表名
        self.port.insert(agentinfo)
      
        return item





    