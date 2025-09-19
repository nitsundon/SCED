import pandas as pd

from classses.ConnectionHandler import MongoConnect


class getSingleInput:
    def __init__(self, dt: str = "04-09-2025"):
        self.db = MongoConnect().getDB()
        self.dt=dt
        self.revision_no=self.getrevision()

    def getrevision(self) -> str:
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
        print(df.iloc[-30:])
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


print(getSingleInput().getRates()[['Generator_Name','Discom_Name','MOD_Rate','MOD_Applicability']])