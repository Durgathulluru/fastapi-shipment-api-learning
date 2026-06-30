# Why use data.py?
#
# data.py separates data-loading and saving logic from the API endpoints
# written in main.py.
#
# shipments.json stores the shipment data permanently.
# This means the data remains available even after the Python program stops.
#
# The JSON file stores shipments as a list of dictionaries.
# Each shipment contains its ID as a normal field:
#
# {
#     "id": 1730,
#     "origin": "New York"
# }
#
# When the application starts, data.py reads that list and creates
# a Python dictionary where each shipment ID becomes the key:
#
# {
#     1730: {
#         "id": 1730,
#         "origin": "New York"
#     }
# }
#
# This dictionary exists only while the application is running.
# It makes it easier to find a shipment directly:
#
# shipments[1730]
#
# POST, PATCH, and DELETE first change this in-memory dictionary.
# Then save() writes those changes back into shipments.json.

# Path is used to represent and work with file paths.
from pathlib import Path

# json is a built-in Python module used to read and write JSON data.
import json


# Create an empty Python dictionary.
# Later, each shipment ID will become a key,
# and the complete shipment record will become its value.
shipments = {}


# Represent the location of the shipments.json file.
# Because only the filename is given, Python looks in the current folder.
file_path = Path("shipments.json")

###print (f"before loading shipments: {shipments}")
# Check whether shipments.json exists before trying to open it.
# If it does not exist, stop the program and show an error.
if not file_path.exists():
    raise FileNotFoundError(
        "shipments.json was not found in the app folder."
    )


# Open shipments.json in read mode.
# The file is automatically closed after the with block finishes.
with open(file_path, "r") as file:

    # Read the JSON file and convert it into Python data.
    # Because the JSON file contains a list of objects,
    # data becomes a Python list of dictionaries.
    data = json.load(file)


# Go through one shipment dictionary at a time.
for record in data:

    # Get the shipment ID from the current record.
    # Use that ID as the key in the shipments dictionary.
    # Store the complete shipment record as its value.
    #
    # Example:
    # shipments1730] = {
    #     "id": 1730,
    #     "origin": "New York",
    #     ...
    # }
    
    shipments[record["id"]] = record #we are mapping the values of the record to the key of the shipments dictionary and which turns out be a list of dictionaries.
###print(f"Loading shipment: {shipments}")

# This function saves the current shipments dictionary
# back into shipments.json.
###print(f"After loading shipments: {shipments}")
def save():

    # Open shipments.json in write mode.
    # Write mode replaces the old file content.
    with open(file_path, "w") as file1:

        # shipments.values() returns only the shipment records,
        # without the outer dictionary keys.
        #
        # list(...) converts those records into a list,
        # matching the original structure of shipments.json.
        #
        # json.dump() converts the Python list into JSON
        # and writes it into the file.
        #
        # indent=4 formats the JSON using four spaces,
        # making the file easier to read.
        json.dump(
            list(shipments.values()),
            file1,
            indent=4
        )


## Application starts
## Uvicorn starts

# → main.py imports shipments from data.py

# → data.py reads shipments.json

# → data.py creates the shipments dictionary

# POST/PATCH/DELETE

# → modify shipments in memory

# → save()

# → write updated data back to shipments.json
