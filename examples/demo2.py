sys.path.append('../havenondemand')

from hodclient import *

hodClient = HODClient("your-api-key", "v1")

hodApp = HODApps.OCR_DOCUMENT
paramArr = {}
paramArr["file"] = "testdata/review.jpg"
paramArr["mode"] = "document_photo"

jobId = hodClient.post_request(paramArr, hodApp, async=True)

if jobId is None:
	error = hodClient.get_last_error();
	for err in error.errors:
		print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
else:
	response = hodClient.get_job_result(jobId)
	if response is None:
		error = hodClient.get_last_error();
		for err in error.errors:
			print "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail)
	else:
		texts = response["text_block"]
		resp = ""
		for text in texts:
			resp += "Recognized text: " + text["text"]
		params = dict()
		params["text"] = resp
		response = hodClient.post_request(params, HODApps.ANALYZE_SENTIMENT, False)
		positives = response["positive"]
		resp = "Positive:\n"
		for pos in positives:
			resp += "Sentiment: " + pos["sentiment"] + "\n"
			if pos.get('topic'):
				resp += "Topic: " + pos["topic"] + "\n"
			resp += "Score: " + "%f " % (pos["score"]) + "\n"
			if pos.get('documentIndex'):
				resp += "Doc: " + str(pos["documentIndex"]) + "\n"
		negatives = response["negative"]
		resp += "Negative:\n"
		for neg in negatives:
			resp += "Sentiment: " + neg["sentiment"] + "\n"
			if neg.get('topic'):
				resp += "Topic: " + neg["topic"] + "\n"
			resp += "Score: " + "%f " % (neg["score"]) + "\n"
			if neg.get('documentIndex'):
				resp += "Doc: " + str(neg["documentIndex"]) + "\n"
		aggregate = response["aggregate"]
		resp += "Aggregate:\n"
		resp += "Sentiment: " + aggregate["sentiment"] + "\n"
		resp += "Score: " + "%f " % (aggregate["score"])
		print resp
