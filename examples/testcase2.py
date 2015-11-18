import sys
sys.path.append('../havenondemand')

from hodclient import *

hodClient = HODClient("your-apikey")

# callback function
def requestCompleted(response,error):
    text = ""
    if error != None:
        for err in error.errors:
            text += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
    else:
        entities = response["entities"]

        for entity in entities:
            if entity["type"] == "companies_eng":
                text += "Company name: " + entity["normalized_text"] + "\n"
            elif entity["type"] == "places_eng":
                text += "Place name: " + entity["normalized_text"] + "\n"
            else:
                text += "People name: " + entity["normalized_text"] + "\n"
    print text

paramArr = {}
paramArr["url"] = "http://www.cnn.com"
paramArr["unique_entities"] = "true"
paramArr["entity_type"] = ["people_eng","places_eng","companies_eng"]

hodClient.GetRequest(paramArr, HODApps.ENTITY_EXTRACTION, async=False, callback=requestCompleted)



