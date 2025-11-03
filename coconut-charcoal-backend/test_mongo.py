from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb://Rashmi:Rashmi2004@cluster0-shard-00-00.viopj7x.mongodb.net:27017,cluster0-shard-00-01.viopj7x.mongodb.net:27017,cluster0-shard-00-02.viopj7x.mongodb.net:27017/?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print("❌ Connection failed:", e)
