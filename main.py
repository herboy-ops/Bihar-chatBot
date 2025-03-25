from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Excel and CSV files
df_consumer = pd.read_excel(r"C:\Users\rahul.k\Downloads\Consumption Pattern Analysis_01_2025.xls", engine="xlrd")
df_office = pd.read_csv(r"C:\Users\rahul.k\_SELECT_om_NAME_AS_OFFICE_NAME_COUNT_cm_CONSUMER_ID_AS_CONSUMER__202503241731.csv")

# Ensure OFFICE_NAME column is clean
df_office["OFFICE_NAME"] = df_office["OFFICE_NAME"].astype(str).str.strip().str.upper()

class ConsumerRequest(BaseModel):
    consumer_number: str

@app.post("/get_consumer_details/")
def get_consumer_details(request: ConsumerRequest):
    consumer_number = request.consumer_number.strip().upper()
    
    # Ensure Consumer Number column exists
    if "Consumer Number" not in df_consumer.columns:
        raise HTTPException(status_code=500, detail="Missing 'Consumer Number' column in data.")

    consumer_record = df_consumer[df_consumer["Consumer Number"].str.upper() == consumer_number]

    if consumer_record.empty:
        raise HTTPException(status_code=404, detail="Consumer not found")

    details = consumer_record.iloc[0].to_dict()

    return {
        "Consumer Name": details.get("Consumer Name", "N/A"),
        "Total Bill": details.get("Total Bill", "N/A"),
        "Last Paid Amt": details.get("Last Paid Amt", "N/A"),
        "Last Paid Date": details.get("Last Paid Date", "N/A"),
        "Consumer Status": details.get("Consumer Status", "N/A"),
        "Load": details.get("Load", "N/A"),
    }

@app.get("/get_office_consumer_count/")
def get_office_consumer_count(office_name: str = Query(..., title="Office Name")):
    office_name_cleaned = office_name.strip().upper()

    # Debugging Step: Print available office names
    print("Available Offices:", df_office["OFFICE_NAME"].unique())

    office_record = df_office[df_office["OFFICE_NAME"] == office_name_cleaned]

    if office_record.empty:
        raise HTTPException(status_code=404, detail=f"Office '{office_name}' not found")

    result = office_record[["OFFICE_NAME", "CONSUMER_COUNT", "CONSUMER_STATUS"]].to_dict(orient="records")
    return result[0] if result else {}

@app.get("/")
async def root():
    return {"message": "Welcome to the Electricity Department API!"}
