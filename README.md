# HODClient Library for Python. V2.0

----
## Overview
HODClient for Python is a utility class, which helps you easily integrate your Python project with HPE Haven OnDemand Services.

Version V2.0 also supports bulk input (source inputs can be an array) where an HOD API is capable of doing so.

----
## Integrate HODClient into Python project
1. Download the HODClient library for Python.
2. Unzip and copy the whole havenondemand folder to your project folder.
OR

1. To install the latest version directly from this github repo:
* *
    pip install git+https://github.com/HPE-Haven-OnDemand/havenondemand-python-v2.0


----
## API References
**Constructor**

    HODClient(apiKey, version = "v1")

*Description:* 
* Creates and initializes a HODClient object.

*Parameters:*
* apiKey: your developer apikey.
* version: Haven OnDemand API version. Currently it only supports version 1. Thus, the default value is "v1".

*Example code:*
##
    from havenondemand.hodclient import *
    hodClient = HODClient("your-apikey")

----
**Function GetRequest**

    GetRequest(paramArr, hodApp, mode, callback)

*Description:* 
* Sends a HTTP GET request to call an Haven OnDemand API.

*Parameters:*
* paramArr: a dictionary dict() containing key/value pair parameters to be sent to a Haven OnDemand API, where the keys are the parameters of that Haven OnDemand API.

>Note: 

>For a parameter with its type is an array<>, the parameter must be defined in an array []. 
>E.g.:
## 
    paramArr = dict()
    paramArr["url"] = "http://www.cnn.com"
    paramArr["entity_type"] = ["people_eng","places_eng","companies_eng"]


* hodApp: a string to identify a Haven OnDemand API. E.g. "extractentities". Current supported APIs are listed in the HODApps class.
* async: True | False. Specifies API call as Asynchronous or Synchronous.
* callback: the name of a callback function, which the HODClient will call back and pass the response from server.

*Response:* 
* Response from the server will be returned via the provided callback function

*Example code:*

## 
    # Call the Entity Extraction API synchronously to find people, places and companies from CNN and BBC websites.
    paramArr = dict()
    paramArr["url"] = ["http://www.cnn.com","http://www.bbc.com"]
    paramArr["entity_type"] = ["people_eng","places_eng","companies_eng"]
    
    paramArr["unique_entities" = "true"
    
    hodClient.GetRequest(paramArr, HODApps.ENTITY_EXTRACTION, False, requestCompleted)

    # callback function
    def requestCompleted(response,error):
        if error != None:
            for err in error.errors:
                result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
        else:
            entities = response["entities"]
            text = ""
            for entity in entities:
                if entity["type"] == "companies_eng":
                    text += "Company name: " + entity["normalized_text"] + "\n"
                elif entity["type"] == "places_eng":
                    text += "Place name: " + entity["normalized_text"] + "\n"
                else:
                    text += "People name: " + entity["normalized_text"] + "\n"
            print text
----
**Function PostRequest**
 
    PostRequest(paramArr, hodApp, async, callback)

*Description:* 
* Sends a HTTP POST request to call a Haven OnDemand API.

*Parameters:*
* paramArr: a dictionary dict() containing key/value pair parameters to be sent to a Haven OnDemand API, where the keys are the parameters of that Haven OnDemand API.

>Note: 

>For a parameter with its type is an array<>, the parameter must be defined in an array []. 
>E.g.:
## 
    paramArr = dict()
    paramArr["url"] = "http://www.cnn.com"
    paramArr["entity_type"] = ["people_eng","places_eng","companies_eng"]


* hodApp: a string to identify an Haven OnDemand API. E.g. "ocrdocument". Current supported apps are listed in the HODApps class.
* async: True | False. Specifies API call as Asynchronous or Synchronous.
* callback: the name of a callback function, which the HODClient will call back and pass the response from server.

*Response:* 
* Response from the server will be returned via the provided $callback function

*Example code:*

## 
    # Call PostRequestion function asynchronously.

    # callback function
    def asyncRequestCompleted(jobID, error):
        if error != None:
            for err in error.errors:
                result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
                print result
        else:
            hodClient.GetJobResult(jobID, requestCompleted)

    # callback function
    def requestCompleted(response, error):
        if error != None:
            for err in error.errors:
                result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
        else:
            texts = response["text_block"]
            for text in texts:
                print "Recognized text: " + text["text"]
    
    paramArr = {}
    paramArr["file"] = "full/path/filename.jpg",
    paramArr["mode"] = "document_photo"

    # Call the OCR Document API asynchronously to scan text from an image file.
    hodClient.PostRequest(paramArr, HODApps.OCR_DOCUMENT, True, asyncRequestCompleted)
    
----
**Function GetJobResult**

    GetJobResult(jobID, callback)

*Description:*
* Sends a request to Haven OnDemand to retrieve content identified by a job ID.

*Parameter:*
* jobID: the job ID returned from an Haven OnDemand API upon an asynchronous call.

*Response:* 
* Response from the server will be returned via the provided callback function

*Example code:*
## 

    # Call GetJobResult function to get content from Haven OnDemand server.

    # callback function
    def requestCompleted(response, error):
        if error != None:
            for err in error.errors:
                result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
        else:
            # walk thru the response

    hodClient.GetJobResult(jobID, requestCompleted)

----
## Define and implement callback functions

# 
When you call the GetRequest() or PostRequest() with the async=True, the response in a callback function will be a string containing a jobID.

    def asyncRequestCompleted(response, error):
        # check error

        # call GetJobResult function with the jobID
    
# 
When you call the GetRequest() or PostRequest() with the async=False or call the GetJobResult(), the response in a callback function will be a JSON object of the actual result from the service.

    def requestCompleted(response, error):
        # check error
        
        # walk thru the response

----
## Demo code 1: 

**Call the Entity Extraction API to extract people and places from cnn.com website with a synchronous GET request**

    from havenondemand.hodclient import *

    hodClient = HODClient("your-apikey")

    # callback function
    def requestCompleted(response,error):
        resp = ""
        if error != None:
            for err in error.errors:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
        else:
            entities = response["entities"]
            for entity in entities:
                if entity["type"] == "companies_eng":
                    resp += "Company name: " + entity["normalized_text"] + "\n"
                elif entity["type"] == "places_eng":
                    resp += "Place name: " + entity["normalized_text"] + "\n"
                else:
                    resp += "People name: " + entity["normalized_text"] + "\n"
        print resp


    paramArr = {}
    paramArr["url"] = "http://www.cnn.com"
    paramArr["unique_entities"] = "true"
    paramArr["entity_type"] = ["people_eng","places_eng","companies_eng"]


    hodClient.GetRequest(paramArr, HODApps.ENTITY_EXTRACTION, False, requestCompleted)

----

## Demo code 2:
 
**Call the OCR Document API to scan text from an image with an asynchronous POST request**

    from havenondemand.hodclient import *

    hodClient = HODClient("your-apikey")

    # callback function
    def asyncRequestCompleted(jobID, error):
        if error != None:
            for err in error.errors:
                result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
                print result
        else:
            hodClient.GetJobResult(jobID, requestCompleted)

    # callback function
    def requestCompleted(response, error):
        resp = ""
        if error != None:
            for err in error.errors:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
        else:
            texts = response["text_block"]
            for text in texts:
                resp += "Recognized text: " + text["text"]
        print resp

    paramArr = {}
    paramArr["file"] = "testdata/review.jpg"
    paramArr["mode"] = "document_photo"

    hodClient.PostRequest(paramArr, HODApps.OCR_DOCUMENT, async=True, callback=asyncRequestCompleted)

----
## License
Licensed under the MIT License.