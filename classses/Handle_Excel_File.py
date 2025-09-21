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
            arr[group_index] = group_df.drop(columns=col).to_dict(orient="records")[0]

        return arr

    def createMutliKeyDict(self, group_object, col=["Generator_Name", "Discom_Name"]):
        arr = {}

        # enforce list type
        if isinstance(col, str):
            col = [col]

        for group_index, group_df in group_object.groupby(col):
            # if grouping by 2 columns, group_index is a tuple (generator, discom)
            if len(col) == 1:
                generator = group_index
                discom = None
            else:
                generator, discom = group_index

            group_df.columns = group_df.columns.map(str)
            data = group_df.drop(columns=col).to_dict(orient="records")[0]

            # build nested dict
            if generator not in arr:
                arr[generator] = {}

            if discom is not None:
                arr[generator][discom] = data
            else:
                arr[generator] = data

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
        df = pd.melt(df, id_vars="Generator_Name",var_name="Discom_Name",value_name="share").dropna().sort_values("Generator_Name").reset_index(drop=True)

        return df
    def getIntraDC(self,dropShareCol=True):
        df=self.getIntraShare()
        df1=pd.read_excel(self.file_path, skiprows=2, sheet_name="GEN_DC_DATA")
        df1.drop(columns="Sl/no", inplace=True)
        df2=df.merge(df1,on=["Generator_Name"])

        for col in range(1, 97):
            df2[col] = round(df2[col] * df2['share']/100,2)
        if dropShareCol:
            df2.drop(columns="share",inplace=True)
        return df2

    def getGenRate(self):
        df=self.getIntraShare()
        df1= pd.read_excel(self.file_path, skiprows=2, sheet_name="GEN_INFO")
        df2 = df.merge(df1, on="Generator_Name",how="inner")
        return df2.drop(columns=[ 'Sl/no',"share"])


    def getMODGenOnly(self):
        df=HandleExcelFile().getGenRate()
        return df[(df['MOD_Rate']*df['MOD_Applicability'])>0].reset_index(drop=True)

    def getNONMODGenOnly(self):
        df=HandleExcelFile().getGenRate()
        return df[~((df['MOD_Rate']*df['MOD_Applicability'])>0)].reset_index(drop=True)

    def getIntraNONMODDC(self):
        df=self.getNONMODGenOnly()
        df1=self.getIntraDC(dropShareCol=True)
        return df.merge(df1,on=["Generator_Name","Discom_Name"])



    def getOAGen(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="OA_REQUISITION_DATA")
        return df[['Generator_Name','Discom_Name','OA_Type','Approval_No','MOD_Rate','MOD_Applicability']]

    def getOAMODGen(self):
        df=self.getOAGen();
        return df[((df['MOD_Rate']*df['MOD_Applicability'])>0)]
    def getOANONMODGen(self):
        df=self.getOAGen();
        return df[~((df['MOD_Rate']*df['MOD_Applicability'])>0)]

    def getCommonGen(self):
        df=self.getIntraDC()
        df1=self.getOAMODGen()
        return df.merge(df1,on="Generator_Name")

    def AllContract(self):
        df=self.getGenRate().drop(columns='share')
        df1=self.getOAGen()
        df2=pd.concat([df1,df])
        return df2

    def getOAReq(self):
        df = pd.read_excel(self.file_path, skiprows=2, sheet_name="OA_REQUISITION_DATA")
        return df


df=HandleExcelFile().getOAReq()

df1=df.groupby(by=["Generator_Name","Discom_Name","Approval_No"])
