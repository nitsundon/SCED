import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from classses.ConnectionHandler import MongoConnect
from classses.Handle_Excel_File import HandleExcelFile

json_string={}

df=pd.read_excel('../data/input.xlsx',skiprows=2)
df.drop(columns="Sl/no",inplace=True)
# Make sure NaN -> None so Mongo can store them
df = df.where(pd.notna(df), None)



print({'gen':json_string})
#
db=MongoConnect().getDB()
revision_collection=db["revisions"]
input_collection = db["gen_info"]
revision_id=HandleExcelFile().getRevision()
# print(revision_id)
# # Insert data
df['revision']=revision_id
json_string=df.to_dict(orient="records")
input_collection.insert_many(json_string)


