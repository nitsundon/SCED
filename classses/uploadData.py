import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from classses.ConnectionHandler import MongoConnect
from classses.Handle_Excel_File import HandleExcelFile

json_string={}

df=HandleExcelFile().getDemand()
print(df)
# revision_id=HandleExcelFile(file_path='../data/input.xlsx').getRevision()
