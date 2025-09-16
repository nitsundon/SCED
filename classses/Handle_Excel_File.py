import datetime

import pandas as pd
from classses.ConnectionHandler import MongoConnect
from datetime import datetime


class HandleExcelFile:
    def __init__(self, file_path='../data/input.xlsx'):
        df = pd.read_excel(file_path)
        # df.drop(columns="Sl/no",inplace=True)
        # Make sure NaN -> None so Mongo can store them
        df = df.where(pd.notna(df), None)
        # json_string=df.to_dict(orient="records")
        date = df.columns[1]
        revision = df.iloc[0, 1]
        self.ret = {
            'date': date,
            'revision_no': revision,

        }

    def getRevision(self):
        db = MongoConnect().getDB()
        revision_collection = db["revisions"]
        where_str=self.ret

        result = revision_collection.update_one(where_str, {"$setOnInsert": self.ret}, upsert=True)
        if result.upserted_id:
            # New document inserted
            return result.upserted_id
        else:
            # Document already existed → fetch its _id
            existing = revision_collection.find_one(self.ret, {"_id": 1})
            print(existing)
            return existing['_id']

    def createDict(self,group_object):
        arr={}
        for group_index, group_df in group_object.groupby("Generator_Name"):
            group_df.columns = group_df.columns.map(str)
            arr[group_index] = group_df.drop(columns="Generator_Name").to_dict(orient="records")

        return arr