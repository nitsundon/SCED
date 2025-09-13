import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

df=pd.read_excel('../data/input.xlsx',skiprows=2)
df.drop(columns="Sl/no",inplace=True)
grouped=df.groupby("Generator_Name",)
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
cursor = collection.find({'MOD_Rate': {'$gt':0},'MOD_Applicability':1},{'_id':0,'Generator_Name':1,'MOD_Rate':1,'MOD_Applicability':1,'ExBusInstalledCapacity':1})   # empty filter {} = get everything
docs = list(cursor)            # convert cursor to a list

print(f"Total docs: {len(docs)}")
df_out = pd.DataFrame(docs)
print(df_out)

import plotly.express as px
import numpy as np
# (Optional) keep only applicable rows
df = df_out[df_out["MOD_Applicability"] == 1].copy()

# Make a readable parent label
df["MOD_Rate_lbl"] = df["MOD_Rate"].round(2).astype(str)  # e.g., "4.31"
rate_order = df.sort_values("MOD_Rate")["MOD_Rate_lbl"].unique().tolist()

# (Optional) add a root
df["All"] = "All Plants"
# bins: <3, [3,4), [4,5], >5
cond = [
    df["MOD_Rate"] < 3,
    (df["MOD_Rate"] >= 3) & (df["MOD_Rate"] < 4),
    (df["MOD_Rate"] >= 4) & (df["MOD_Rate"] <= 5),
    df["MOD_Rate"] > 5,
]
choices = ["<3", "3-4", "4-5", ">5"]
df["Rate_Bin"] = np.select(cond, choices, default="unbinned")
rate_order = df.sort_values("Rate_Bin")["MOD_Rate_lbl"].unique().tolist()

print(df.columns)
fig = px.sunburst(
    df,
    path=["All", "MOD_Rate_lbl", "Generator_Name"],   # hierarchy: root → rate → unit
    values="ExBusInstalledCapacity",
    # color="MOD_Rate_lbl"  # uncomment if you want colors by MOD_Rate group
)
# Force ascending order by setting category order
fig.update_traces(
    sort=False
)
fig.update_layout(
    sunburstcolorway=px.colors.qualitative.Set3,
    uniformtext=dict(minsize=10, mode="hide")
)
fig.update_xaxes(categoryorder="array", categoryarray=rate_order)
fig.show()