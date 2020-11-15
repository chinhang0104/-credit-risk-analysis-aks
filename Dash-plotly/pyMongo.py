from pymongo import MongoClient

URL_Mongo = 'your-key'
client = MongoClient(URL_Mongo)

# Accessing Database
print(client.list_database_names())
# db.client['database_name']
