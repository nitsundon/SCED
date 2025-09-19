import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from classses.ConnectionHandler import MongoConnect
from classses.Handle_Excel_File import HandleExcelFile

json_string={}
handler=HandleExcelFile()
revision_id=handler.getRevision()
geninfo=handler.createDict(handler.getGenRate())
dc=handler.createDict(handler.getIntraDC())
demand=handler.getDemand()
nonmod=handler.createDict(handler.getIntraNONMODDC())


json_string['revision_id']=revision_id
json_string['info']=geninfo
json_string['fixed']=handler.createDict(handler.getIntraNONMODDC())
json_string['demand']=handler.getDemand()
json_string['dc']=handler.createDict(handler.getIntraDC(),col=["Generator_Name","Discom_Name"])
db=MongoConnect().getDB()
db['parameters'].update_one({'revision_id':revision_id}, {"$setOnInsert": json_string}, upsert=True)


