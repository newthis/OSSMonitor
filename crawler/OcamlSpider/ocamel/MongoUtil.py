# -*- coding:utf-8 -*-
import ssl
import json
import pymongo
import traceback
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class MongoUtil:


    #headers = {'content-type': 'application/json'}
    def __init__(self,addr, port):
        self.addr = addr
        self.port = port


    def connect(self):
        # socketKeepAlive = True
        self.mongoClient = pymongo.MongoClient(self.addr, self.port, socketKeepAlive = True, serverSelectionTimeoutMS = 6000)


    def close(self):
        if self.mongoClient is not None:
            self.mongoClient.close()

    def updateOneDoc(self, dbName, collectionName, docIndicate, updateContent):
        try:
            if self.mongoClient is not None:
                db = self.mongoClient.get_database(dbName)
                collection = db.get_collection(collectionName)
                collection.update_one(docIndicate, updateContent)

                return 1
            return -1
        except Exception,e:
            msg = traceback.format_exc()
            print msg
            return -1

    def saveDoc(self, dbName, collectionName, doc):
        try:
            if self.mongoClient is not None:
                db = self.mongoClient.get_database(dbName)
                collection = db.get_collection(collectionName)
                collection.save(doc)

                return 1
            return -1
        except Exception,e:
            msg = traceback.format_exc()
            print msg
            return -1




    def insertOneDoc(self,dbName,collectionName, docContnet):
        try:
            db = self.mongoClient.get_database(dbName)
            collection = db.get_collection(collectionName)
            collection.insert(docContnet)

            return 1
        except Exception,e:
            print e.message
            return -1


    def insertManyDoc(self,dbName,collectionName, docContnet):
        try:
            db = self.mongoClient.get_database(dbName)
            collection = db.get_collection(collectionName)
            collection.insert_many(docContnet)



            return 1
        except Exception,e:
            print e.message
            return -1

    # def exeucteQuery(self, dbName, collectionName, query):
    #     try:
    #         db = self.mongoClient.get_database(dbName)
    #         collection = db.get_collection(collectionName)
    #         result = collection.find(query)
    #     except Exception, e:
    #
    #         print e.message



    def getAll(self,dbName, collectionName):
        try:
            db = self.mongoClient.get_database(dbName)
            collection = db.get_collection(collectionName)

            result = collection.find()
            return result
        except Exception,e:
            print e.message
            return None


    def getResultForQuery(self, dbName, collectionName, query):
        try:
            db = self.mongoClient.get_database(dbName)
            collection = db.get_collection(collectionName)
            result = collection.find(query)
            return result
        except Exception,e:
            stds =traceback.format_exc()
            print stds
            return None



