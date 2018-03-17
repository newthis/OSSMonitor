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
from ocamel.items import OcamelItem
from ocamel.items import OcamlVersionItem
import pymongo
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class OcamelPipeline(object):
    def __init__(self):
        print 'OcamelPipeline'
        self.mongoClient = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT, socketKeepAlive = True, serverSelectionTimeoutMS = 6000)

    def __del__(self):
        if self.mongoClient is not None:
            self.mongoClient.close()


    def process_item(self, item, spider):
        db = self.mongoClient.get_database('Ocamel')
        colc = db.get_collection('ocamel')

        if isinstance(item, OcamelItem):

            projectUrl = item['data']['project_url']
            co = colc.find({"project_url":projectUrl}).count()
            if co == 0:
                colc.insert(item['data'])
            else:
                uts = colc.find({"project_url": projectUrl})
                vss = item['data']['versions']
                newest = vss[0]
                if len(newest['name']) > 0:
                    for ut in uts:
                        previous = ut['versions']
                        for pp in previous:
                            if pp['name'] != newest['name']:
                                item['data']['versions'].append(pp)
                        colc.update({"project_url": item['data']['project_url']}, {"$set": item['data']})


        elif isinstance(item, OcamlVersionItem):
            urls = item['data']['project_url']
            indics = colc.find({"project_url": urls.strip()}).count()
            if indics == 0:
                del item['data']['project_url']
                newdict = {}
                newdict['project_url'] = urls
                newdict['versions'] = [item['data']]
                colc.insert(newdict)
            else:
                del item['data']['project_url']
                prt = item['data']['name']
                if len(prt.strip()) > 0:
                    results = colc.find({"project_url": urls.strip()})
                    for rs in results:
                        newVList = []
                        vers = rs['versions']
                        for ver in vers:
                            if ver['name'] != prt:
                                newVList.append(ver)

                        newVList.append(item['data'])
                        rs['versions'] = newVList
                        colc.update({"project_url": rs['project_url']}, {"$set": rs})


