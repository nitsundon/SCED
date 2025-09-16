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
        self.file_path=file_path

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

    def createDict(self,group_object,col="Generator_Name"):
        arr={}
        for group_index, group_df in group_object.groupby(col):
            group_df.columns = group_df.columns.map(str)
            arr[group_index] = group_df.drop(columns=col).to_dict(orient="records")

        return arr

    def getCentre(self,utility="Discom"):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="CENTRE")
        df.drop(columns="Sl/no", inplace=True)
        print(df)
        # Make sure NaN -> None so Mongo can store them
        if utility=="Discom":
            df1=df[df['Generator_Name']=="Power_Exchange"]
            df1.drop(columns="Generator_Name",inplace=True)
            return self.createDict(df1,"Discom_Name" )
        else:
            df1 = df[df['Discom_Name'] == "Centre"]
            df1.drop(columns="Discom_Name")
            return self.createDict(df1, "Generator_Name")
    def getRTM(self,utility="Discom"):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="RTM")
        df.drop(columns="Sl/no", inplace=True)
        print(df)
        # Make sure NaN -> None so Mongo can store them
        if utility=="Discom":
            df1=df[df['Generator_Name']=="RTM"]
            df1.drop(columns="Generator_Name",inplace=True)
            return self.createDict(df1,"Discom_Name" )
        else:
            df1 = df[df['Discom_Name'] == "RTM"]
            df1.drop(columns="Discom_Name")
            return self.createDict(df1, "Generator_Name")

    def getPX(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="PX")
        df.drop(columns="Sl/no", inplace=True)
        df=df[~(df['Discom_Name']=="Power_Exchange")]
        df.drop(columns="Generator_Name",inplace=True)
        return self.createDict(df,"Discom_Name" )
    def getREMC(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="REMC")
        df.drop(columns="Sl/no", inplace=True)
        return self.createDict(df,"Discom_Name" )

    def getDemand(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="DISCOM_DEMAND_DATA")
        df.drop(columns="Sl/no", inplace=True)
        return self.createDict(df,"Discom_Name" )

    def getIntraDiscomTrade(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="INTRA_DISCOM_TRADE")
        df.drop(columns="Sl/no", inplace=True)
        return self.createDict(df, "Discom_Name")

    def getStandby(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="STAND_BY")
        df.drop(columns="Sl/no", inplace=True)
        return self.createDict(df, "Discom_Name")


    def getIntraShare(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="GEN_DISCOM_SHARE")
        df=df.drop(columns="Sl/no")
        df = pd.melt(df, id_vars="Generator_Name").dropna().sort_values("Generator_Name").reset_index(drop=True)

        return df
    def getIntraDC(self):
        df=self.getIntraShare()
        df1=pd.read_excel(self.file_path, skiprows=2, sheet_name="GEN_DC_DATA")

        return df.merge(df1,on="Generator_Name")

df=HandleExcelFile().getIntraDC()


print(df.iloc[-25:])