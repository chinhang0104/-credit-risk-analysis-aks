from pymongo import MongoClient
import pprint as pp

# change you key to the correct one
URL_Mongo = 'mongodb://Msbd5003-mongodb:zsETiWDaAJdqODfOg62miplS9kHMEs5N5xhmgyIzSzEaOKVfMdJp7IUThBqd7obK1OBsnR1n2hHqMdORMCCx6w==@msbd5003-mongodb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@msbd5003-mongodb@'
client = MongoClient(URL_Mongo)

# Accessing Database
print(client.list_database_names())
db_credit = client['credit']

# Collection - application
print(db_credit.list_collection_names())
db_credit_application = db_credit['application']

pp.pprint(db_credit_application.count_documents({}))

documents = db_credit_application.find({"NAME_CONTRACT_TYPE" : "Revolving loans"})
pp.pprint(documents[0])

pp.pprint(db_credit_application.count_documents({"NAME_CONTRACT_TYPE" : "Revolving loans"}))

# Collection - installment
print(db_credit.list_collection_names())
db_credit_installment = db_credit['installment']

documents = db_credit_installment.find({})
pp.pprint(documents)

# Collection - prev_application
print(db_credit.list_collection_names())
db_credit_prev_application = db_credit['prev_application']

documents = db_credit_prev_application.find({})
pp.pprint(documents[0])
pp.pprint(db_credit_prev_application.find_one())
