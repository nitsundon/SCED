import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
json_string={}
df=pd.read_excel('../data/input.xlsx',skiprows=2)
df.drop(columns="Sl/no",inplace=True)
# Make sure NaN -> None so Mongo can store them
df = df.where(pd.notna(df), None)
json_string=df.to_dict(orient="records")
uri = "mongodb+srv://niteshsunildongre_db_user:CAVSdrZTnNMKZGSk@cluster0.cwebq8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
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
db = client["sced"]
collection = db["inputs"]

# Insert data
collection.insert_one({'geninfo':json_string})


