import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

class MongoConnect:
    def __init__(self,db="sced"):
        self.pwd="CAVSdrZTnNMKZGSk"
        self.db=db
        uri = f'mongodb+srv://niteshsunildongre_db_user:{self.pwd}@cluster0.cwebq8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
        # Create a new client and connect to the server
        client = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),              # <- trust store fix
            serverSelectionTimeoutMS=30000
        )
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        # Select database and collection
        self.db_instance = client[self.db]

    def getDB(self):
        return self.db_instance