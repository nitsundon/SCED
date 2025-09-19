import pandas as pd

from classses.ConnectionHandler import MongoConnect


class getSingleInput:
    def __init__(self, dt= "04-09-2025",db=None):

        self.dt=dt
        self.db = db
        if self.db is None:
            self.db=MongoConnect().getDB()

        self.revision_no=self.getrevision()

    def getrevision(self) -> str:
        print(self.dt)
        revision_id = self.db['revisions'].find({'date': self.dt}, {'_id': 1}).sort({'revision_no':-1}).limit(1)
        return list(revision_id)[0]['_id']

    def getDC(self):
         # fetch document from MongoDB
        cursor = self.db['parameters'].find_one(
            {'revision_id': self.revision_no},
            {'dc': 1, '_id': 0}
        )

        if not cursor or 'dc' not in cursor:
            print("No DC data found")
            return pd.DataFrame()

        data = cursor['dc']  # <-- use the actual MongoDB dc dict

        records = []
        for gen, discoms in data.items():
            for discom, values in discoms.items():
                record = {"Generator_Name": gen, "Discom_Name": discom}
                record.update(values)  # flatten MW, Price, etc.
                records.append(record)

        df = pd.DataFrame(records)

        return df

    def getRates(self):
        # fetch document from MongoDB
        cursor = self.db['parameters'].find_one(
            {'revision_id': self.revision_no},
            {'info': 1, '_id': 0}
        )

        if not cursor or 'info' not in cursor:
            print("No info data found")
            return pd.DataFrame()

        data = cursor['info']  # <- your nested dict

        records = []
        for gen, values in data.items():
            record = {"Generator_Name": gen}
            record.update(values)  # merge Discom_Name, share, MOD_Rate, etc.
            records.append(record)

        df = pd.DataFrame(records)

        return df

    def getDCwithRate(self):
        df1=self.getRates().drop(columns=["Discom_Name"])
        df2=self.getDC()
        df3=df1.merge(df2,on="Generator_Name")
        df3.drop(columns=["InsgsType","Company","InstalledCapacity","ExBusInstalledCapacity"],inplace=True)
        df3=df3[df3['MOD_Rate']*df3['MOD_Applicability']>0].drop(columns="MOD_Applicability")
        df3=df3.melt(id_vars=["Generator_Name","Discom_Name","MOD_Rate"],var_name="Block",value_name="MW")
        return df3

