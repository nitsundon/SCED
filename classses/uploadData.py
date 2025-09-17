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


json_string['revision']=revision_id
json_string['info']=geninfo





