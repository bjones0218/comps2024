from pymongo import MongoClient
import datetime


# NOTES: TO DUMP A DB
# run the command: mongodump --uri="mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2" which will dump all data from all collections
# THIS SHOULD BE DONE ONCE WE HAVE FILLED IN THE DB
# 

# TO RESTORE A DB
# run the command: mongorestore dump (as long as dump is in this directory, if not you have to give the path)


# This is a document created by Marc Eidelhoch to give a basic example of how to use MongoDB
# This example is based on being a store owner

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2"

client = MongoClient(CONNECTION_STRING)

# In MongoDB a database is like a big container for an entire project for example
# In this example we have a single database for the entire store
store_test_db = client["store_test"]

if store_test_db["customers"] is not None:
    store_test_db.drop_collection("customers")

if store_test_db["inventory"] is not None:
    store_test_db.drop_collection("inventory")

if store_test_db["suppliers"] is not None:
    store_test_db.drop_collection("suppliers")

# While a collection is like a table for related things
# In this example we have collections for customers, inventory and suppliers
customer_collection = store_test_db["customers"]
inventory_collection = store_test_db["inventory"]
suppliers_collection = store_test_db["suppliers"]

# Here we create customers to add to the database
customer1 = {"name": "Marc", "age": 22, "occupation": "Student", "hometown": "San Francisco"}
customer2 = {"name": "Blake", "age": 12, "occupation": "Ninja", "hometown": "Des Moines"}
customer3 = {"name": "Luke", "age": 5, "occupation": "Cool", "hometown": "Food Desert"}
customer4 = {"name": "Sam", "age": 35, "occupation": "Baseballer", "hometown": "Glencoe"}

# We can insert to a collection 1 at a time:
customer_collection.insert_one(customer1)

# Or multiple at a time:
customers = [customer2, customer3, customer4]
customer_collection.insert_many(customers)

# We can query for an individual customer
print(customer_collection.find_one({"name": "Marc"}))

# We can print everything in the collection
for customer in customer_collection.find():
    print(customer)

# Note that we do not need to have the same "column names" or even any in common
inventory1 = {"item_name": "Apple", "quantity": 13, "color": "Red"}
inventory2 = {"item_num": 35211, "size": "Medium", "brand": "Patagonia"}
inventory3 = {"genre": "Country", "artist": "Zach Bryan", "release_date": datetime.datetime(2018, 11, 23)}

inventory = [inventory1, inventory2, inventory3]

inventory_collection.insert_many(inventory)

# If you look for something that doesn't exist:
print(inventory_collection.find_one({"item_name": "Shirt"}))

# You can update values
print(inventory_collection.find_one({"item_name": "Apple"}))
# Increases it by one
print(inventory_collection.update_one({"item_name": "Apple"}, {"$inc": { "quantity" : 1} }))
print(inventory_collection.find_one({"item_name": "Apple"}))


supplier1 = {"supplier_name": "Old Navy"}

suppliers_collection.insert_one(supplier1)

print(suppliers_collection.find_one({"supplier_name": "Old Navy"}))
# Change the name
print(suppliers_collection.update_one({"supplier_name": "Old Navy"}, {"$set": { "supplier_name" : "New Navy"} }))
print(suppliers_collection.find_one({"supplier_name": "New Navy"}))


print(client.list_database_names())



