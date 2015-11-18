import sys
sys.path.append('../havenondemand')

from hodclient import *

hodClient = HODClient("your-apikey")
hodApp = ""
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
			resp = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
	else:
		if hodApp == HODApps.RECOGNIZE_SPEECH:
			documents = response["document"]
			for doc in documents:
				resp += doc["content"] + "\n"
				if "offset" in doc:
					resp += "%d" % (doc["offset"])
					resp += "\n"
		elif hodApp == HODApps.OCR_DOCUMENT:
			texts = response["text_block"]
			for text in texts:
				resp += "Recognized text: " + text["text"]
	print resp

paramArr = {}
hodApp = HODApps.RECOGNIZE_SPEECH

if hodApp == HODApps.RECOGNIZE_SPEECH:
    paramArr["file"] = "testdata/attendant.mp3"
elif hodApp == HODApps.OCR_DOCUMENT:
    paramArr["file"] = "testdata/review.jpg"
    paramArr["mode"] = "document_photo"

hodClient.PostRequest(paramArr, hodApp, async=True, callback=asyncRequestCompleted)



