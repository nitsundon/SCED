from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://niteshsunildongre_db_user:CAVSdrZTnNMKZGSk@cluster0.cwebq8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
import certifi
client = MongoClient(uri, tlsCAFile=certifi.where())
print(client.admin.command("ping"))

client.get_database()