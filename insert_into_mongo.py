import pandas as pd
from pymongo import MongoClient

# Function to upload CSV data to MongoDB
def csv_to_mongodb(csv_file_path, collection_name, uri):
    """
    Reads a CSV file and inserts it into a specified collection in the MongoDB database.

    Args:
    csv_file_path (str): Path to the CSV file.
    collection_name (str): The name of the collection to create or use.
    uri (str): The MongoDB connection URI.

    Returns:
    None
    """
    # Read the CSV file into a DataFrame
    try:
        data = pd.read_csv(csv_file_path)
        print(f"Successfully read the CSV file: {csv_file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}. Please check the path and try again.")
        return
    except pd.errors.ParserError:
        print("Error: Unable to parse the CSV file. Check the file format.")
        return

    # Connect to MongoDB using the provided URI
    try:
        client = MongoClient(uri)
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # Access the specified database and collection
    db = client['influencers']
    collection = db[collection_name]

    # Insert data into the collection
    try:
        collection.insert_many(data.to_dict("records"))
        print(f"Successfully inserted {len(data)} records into the '{collection_name}' collection in 'allLeads' database.")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

# Replace with your details
csv_file_path = "all_leads_from_muslim_campaigns_filtered.csv"  # Replace with the path to your CSV file
collection_name = "muslim_influencers"     # Replace with the collection name you want to create
db_password = "XWtqSgOf8a6pTasP"                # Replace with your MongoDB password
username = "lokosalmond"                     # Replace with your MongoDB username
cluster_url = "allleads.mynvr.mongodb.net"    # Replace with your MongoDB cluster URL

# Build the MongoDB connection URI
uri = f"mongodb+srv://{username}:{db_password}@{cluster_url}/?retryWrites=true&w=majority&appName=allLeads"

# Call the function to upload the CSV data
csv_to_mongodb(csv_file_path, collection_name, uri)
