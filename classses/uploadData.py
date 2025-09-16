import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from classses.ConnectionHandler import MongoConnect
from classses.Handle_Excel_File import HandleExcelFile

json_string={}

df=pd.read_excel('../data/input.xlsx',skiprows=2,sheet_name="GEN_DC_DATA")
df.drop(columns="Sl/no",inplace=True)
# Make sure NaN -> None so Mongo can store them
df = df.where(pd.notna(df), None)

revision_id=HandleExcelFile(file_path='../data/input.xlsx').getRevision()
