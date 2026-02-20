#this is a demo project of finding gender
import csv
import os
import requests
from datetime import datetime

def load_existing_names(filename):
    existing = set()

    if not os.path.exists(filename):
        return existing
    
    with open(filename, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name=row.get("name")

            if name:
                existing.add(name.strip().lower())

    return existing

    

def get_user_input(existing_names):

    while(True):
        user_input = input("Enter name (or type 'exit' to stop) :").strip()

        if user_input.lower()=="exit":
            return None
        
        if not user_input:
            print("Can't take expty input .try again..")
            continue
        
        normalized_name = user_input.lower()

        if normalized_name in existing_names:
            print("Name already exists. Skipping...")
            continue

        return normalized_name
       


def fetch_data(name):

    url ="https://api.genderize.io/"

    try:
        response = requests.get(url,params={"name":name}, timeout=5)
        response.raise_for_status()
        return response.json()

      

    except requests.exceptions.RequestException as e:
        print(f"Request failed. {e}")
        return None
    
    except ValueError:
        print("Invalid Json received.")
        return None



def process_data(data):
    if not data:
        return None
    
    recquired_fields = ["name", "gender","probability","count"]

    for field in recquired_fields:
        if field not in data:
            print("Unexpected API response structure .")
            return None
        
        if data["gender"] is None:
            print("No gender prediction availbale. Skipping.")
            return None
        
        record = {
            "name": data["name"].strip().lower(),
            "predicted_gender": data["gender"],
            "probability":data["probability"],
            "sample_count":data["count"],
            "fetched_at":datetime.now().isoformat()

        }
    return record
        
        


def save_to_csv(record, filename):

    file_exists = os.path.exists(filename)

    with open(filename, "a",newline="")as f:
        writer = csv.DictWriter(f, fieldnames=["name","predicted_gender","probability","sample_count","fetched_at"])
       
        if not file_exists:
            writer.writeheader()


        writer.writerow(record)

    print("Saved record successfully.")



def main():
    filename = "records.csv"

    existing_names=load_existing_names(filename)

    while True:

        name=get_user_input(existing_names)

        if name is None:
            print("Existing program.")
            break

        raw_data = fetch_data(name)
        if not raw_data:
            continue

        record=process_data(raw_data)
        if not record:
            continue
        save_to_csv(record , filename)

        existing_names.add(name)

if __name__ == "__main__":
    main()