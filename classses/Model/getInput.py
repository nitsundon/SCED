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
        df=pd.DataFrame()
        print(self.revision_no)
        cursor=self.db['parameters'].find_one({'revision_id':self.revision_no},{'dc':1,'_id':0})
        dc_list=cursor['dc']
        df = pd.DataFrame(dc_list).T

        print(df[(df['Discom_Name']=="TPCL") ])



getSingleInput().getDC()