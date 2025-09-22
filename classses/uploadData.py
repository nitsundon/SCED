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
json_string['demand']=handler.getDemand()
json_string['dc']=handler.createMutliKeyDict(handler.getIntraDC(),col=["Generator_Name","Discom_Name"])
json_string['px']=handler.getPX()
json_string['remc']=handler.getREMC()
json_string['centre']=handler.getCentre()
json_string['rtm']=handler.getRTM()
json_string['standby']=handler.getStandby()
json_string['interdiscom']=handler.getIntraDiscomTrade()
# json_string['oa_req']=handler.createMultikeyDictNew(handler.getOAReq(),col=["type","Discom_Name","Generator_Name","Approval_No"])
json_string['oa_req']=handler.getOAReq().to_dict(orient="records")
json_string['pmin_intra']=handler.createDict(handler.getPminofIntra(contract_type="intra"))
json_string['pmin_oa']=handler.createMutliKeyDict(handler.getPminofIntra(contract_type="oa"),col=["Generator_Name","Approval_No"])

json_string['rampup']=handler.createDict(handler.getRamp())
json_string['rampdown']=handler.createDict(handler.getRamp(direction="down"))



db=MongoConnect().getDB()
db['parameters'].update_one({'revision_id':revision_id}, {"$setOnInsert": json_string}, upsert=True)


