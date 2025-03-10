import requests
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()

# Google Authentication
PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = os.getenv('DATASET_ID')
TABLE_ID = 'vend_sales'

# Replace with the path to your service account key file
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

# Initialize BigQuery client
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

# Define the BigQuery table reference
dataset_ref = client.dataset(DATASET_ID)
table_ref = dataset_ref.table(TABLE_ID)

# Define the schema of the BigQuery table
schema = [
    bigquery.SchemaField("id", "STRING"),
    bigquery.SchemaField("outlet_id", "STRING"),
    bigquery.SchemaField("register_id", "STRING"),
    bigquery.SchemaField("user_id", "STRING"),
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("invoice_number", "STRING"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("source_id", "STRING"),
    bigquery.SchemaField("complete_open_sequence_id", "STRING"),
    bigquery.SchemaField("accounts_transaction_id", "STRING"),
    bigquery.SchemaField("has_unsynced_on_account_payments", "STRING"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("note", "STRING"),
    bigquery.SchemaField("short_code", "STRING"),
    bigquery.SchemaField("return_for", "STRING"),
    bigquery.SchemaField("return_ids", "STRING", mode="REPEATED"),
    bigquery.SchemaField("total_loyalty", "FLOAT"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
    bigquery.SchemaField("sale_date", "TIMESTAMP"),
    bigquery.SchemaField("deleted_at", "TIMESTAMP"),
    bigquery.SchemaField("line_items", "RECORD", mode="REPEATED", fields=[
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("salesperson_id", "STRING"),
        bigquery.SchemaField("tax_id", "STRING"),
        bigquery.SchemaField("discount_total", "FLOAT"),
        bigquery.SchemaField("discount", "FLOAT"),
        bigquery.SchemaField("price_total", "FLOAT"),
        bigquery.SchemaField("price", "FLOAT"),
        bigquery.SchemaField("cost_total", "FLOAT"),
        bigquery.SchemaField("cost", "FLOAT"),
        bigquery.SchemaField("tax_total", "FLOAT"),
        bigquery.SchemaField("tax", "FLOAT"),
        bigquery.SchemaField("quantity", "FLOAT"),
        bigquery.SchemaField("loyalty_value", "FLOAT"),
        bigquery.SchemaField("note", "STRING"),
        bigquery.SchemaField("price_set", "BOOLEAN"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("sequence", "INTEGER"),
        bigquery.SchemaField("gift_card_number", "STRING"),
        bigquery.SchemaField("tax_components", "RECORD", mode="REPEATED", fields=[
            bigquery.SchemaField("rate_id", "STRING"),
            bigquery.SchemaField("total_tax", "FLOAT"),
        ]),
        bigquery.SchemaField("promotions", "STRING", mode="REPEATED"),
        bigquery.SchemaField("surcharges", "STRING", mode="REPEATED"),
        bigquery.SchemaField("unit_loyalty_value", "FLOAT"),
        bigquery.SchemaField("total_discount", "FLOAT"),
        bigquery.SchemaField("total_loyalty_value", "FLOAT"),
        bigquery.SchemaField("unit_cost", "FLOAT"),
        bigquery.SchemaField("unit_discount", "FLOAT"),
        bigquery.SchemaField("unit_price", "FLOAT"),
        bigquery.SchemaField("unit_tax", "FLOAT"),
        bigquery.SchemaField("total_tax", "FLOAT"),
        bigquery.SchemaField("total_price", "FLOAT"),
        bigquery.SchemaField("total_cost", "FLOAT"),
        bigquery.SchemaField("is_return", "BOOLEAN"),
    ]),
    bigquery.SchemaField("payments", "RECORD", mode="REPEATED", fields=[
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("register_id", "STRING"),
        bigquery.SchemaField("register_open_sequence_id", "STRING"),
        bigquery.SchemaField("outlet_id", "STRING"),
        bigquery.SchemaField("retailer_payment_type_id", "STRING"),
        bigquery.SchemaField("payment_type_id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("amount", "FLOAT"),
        bigquery.SchemaField("payment_date", "TIMESTAMP"),
        bigquery.SchemaField("deleted_at", "TIMESTAMP"),
        bigquery.SchemaField("external_attributes", "STRING", mode="REPEATED"),
        bigquery.SchemaField("external_applications", "STRING", mode="REPEATED"),
        bigquery.SchemaField("surcharge", "FLOAT"),
        bigquery.SchemaField("source_id", "STRING"),
    ]),
    bigquery.SchemaField("adjustments", "STRING", mode="REPEATED"),
    bigquery.SchemaField("external_applications", "STRING", mode="REPEATED"),
    bigquery.SchemaField("attributes", "STRING", mode="REPEATED"),
    bigquery.SchemaField("version", "INTEGER"),
    bigquery.SchemaField("ecom_custom_charges", "RECORD", fields=[
        bigquery.SchemaField("charges", "STRING", mode="REPEATED"),
        bigquery.SchemaField("total", "FLOAT"),
        bigquery.SchemaField("total_incl", "FLOAT"),
        bigquery.SchemaField("total_tax", "FLOAT"),
    ]),
    bigquery.SchemaField("taxes", "RECORD", mode="REPEATED", fields=[
        bigquery.SchemaField("amount", "FLOAT"),
        bigquery.SchemaField("id", "STRING"),
    ]),
    bigquery.SchemaField("total_tax", "FLOAT"),
    bigquery.SchemaField("total_price", "FLOAT"),
    bigquery.SchemaField("receipt_number", "STRING"),
    bigquery.SchemaField("total_price_incl", "FLOAT"),
    bigquery.SchemaField("total_surcharge", "FLOAT"),
]

# Create the table if it doesn't exist
table = bigquery.Table(table_ref, schema=schema)
table = client.create_table(table, exists_ok=True)

# Function to fetch data from Vend API
def fetch_vend_data(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Function to load data into BigQuery
def load_data_to_bigquery(client, table_ref, rows_to_insert):
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"Encountered errors while inserting rows: {errors}")
    else:
        print("Data successfully inserted into BigQuery.")

# Vend API details
vend_url = "https://ashcorp.retail.lightspeed.app/api/2.0/sales"
vend_headers = {
    "accept": "application/json",
    "authorization": f"Bearer {os.getenv('LIGHTSPEED_ACCESS_TOKEN')}"
}

# Pagination parameters
after = 0

# Extract, Transform, Load (ETL) process
while True:
    # Extract data from Vend API
    params = {"after": after}
    data = fetch_vend_data(vend_url, vend_headers, params)
    
    # Transform data (if needed)
    rows_to_insert = data["data"]
    
    # Load data into BigQuery
    load_data_to_bigquery(client, table_ref, rows_to_insert)
    
    # Get the max version number for the next request
    after = data["version"]["max"]
    
    # Check if the data collection is empty
    if not data["data"]:
        break

print("ETL process completed successfully.")
