import pandas as pd
from classses.ConnectionHandler import MongoConnect


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
        result = revision_collection.update_one(self.ret, {"$setOnInsert": self.ret}, upsert=True)
        if result.upserted_id:
            # New document inserted
            return result.upserted_id
        else:
            # Document already existed → fetch its _id
            existing = revision_collection.find_one(self.ret, {"_id": 1})
            print(existing)
            return existing['_id']
