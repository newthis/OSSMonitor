# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.files import FilesPipeline
from os.path import basename,dirname,join
from urlparse import urlparse
import settings
from lua.items import LuaItem
import pymongo
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class LuaPipeline(object):
    def __init__(self):
        print 'LuaPipeline'
        self.mongoClient = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT, socketKeepAlive = True, serverSelectionTimeoutMS = 6000)

    def __del__(self):
        if self.mongoClient is not None:
            self.mongoClient.close()


    def process_item(self, item, spider):
        db = self.mongoClient.get_database('LuaLocks')
        colc = db.get_collection('lua')
        if isinstance(item, LuaItem):
            projectUrl = item['data']['project_url']
            co = colc.find({"project_url":projectUrl}).count()
            if co == 0:
                colc.insert(item['data'])
            else:
                colc.update({"project_url":item['data']['project_url']}, {"$set":item['data']})

