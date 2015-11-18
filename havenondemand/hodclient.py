import requests
import json
from requests.exceptions import ConnectionError

proxyDict = {
	# "http"  : http_proxy,
	# "https" : https_proxy,
	# "ftp"   : ftp_proxy
}
class ErrorCode:
	TIMEOUT = 1600
	IN_PROGRESS = 1610
	QUEUED = 1620
	HTTP_ERROR = 1630
	CONNECTION_ERROR = 1640
	IO_ERROR = 1650
	INVALID_PARAM = 1660

class HODErrorObject:
	error = 0
	reason = ""
	detail = ""

class HODErrors:
	errors = []
	def addError(self, error):
		self.errors.append(error)

	def resetErrorList(self):
		self.errors = []

class HODClient(object):
	hodEndPoint = "http://api.havenondemand.com/1/api/"
	hodJobResult = "http://api.havenondemand.com/1/job/result/"
	apiVersion = "v1"
	apiKey = None
	proxy = None
	errorsList = HODErrors()

	def __init__(self, apikey, apiversion="v1", proxy={}):
		self.apiVersion = apiversion
		self.apiKey = apikey
		self.proxy = proxy

	def GetJobResult(self, jobId, callback):
		queryStr = "%s%s?apikey=%s" % (self.hodJobResult, jobId, self.apiKey)
		try:
			response = requests.get(queryStr, verify=False, timeout=600)
			if response.status_code != 200:
				jsonObj = json.loads(response.text)
				print jsonObj
				self.__parseHODResponse(jsonObj)
				callback("", self.errorsList)
			else:
				resp = self.__parseHODResponse(response.json())
				if resp == "queued":
					callback("", self.errorsList)
				elif resp == "in progress":
					callback("", self.errorsList)
				elif resp == "errors":
					callback("", self.errorsList)
				else:
					callback(resp, None)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "timeout")
			callback ("", self.errorsList)
		except requests.HTTPError:
			self.__createErrorObject(ErrorCode.HTTP_ERROR, "HTTP error")
			callback ("", self.errorsList)
		except ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error")
			callback ("", self.errorsList)

	def PostRequest(self, params, hodApp, async, callback):
		queryStr = self.hodEndPoint
		if async is True:
			queryStr += "async/%s/%s" % (hodApp, self.apiVersion)
		else:
			queryStr += "sync/%s/%s" % (hodApp, self.apiVersion)
		data = list()
		data.append(("apikey", self.apiKey))
		files = list()
		for key, value in params.items():
			if isinstance(value, list):
				if key == "file":
					for i, vv in enumerate(value):
						try:
							f = open(vv, 'rb')
							files.append((key, f))
						except IOError:
							self.__createErrorObject(ErrorCode.IO_ERROR, "File not found")
							callback("", self.errorsList)
							return
				else:
					for vv in value:
						data.append((key, vv))
			else:
				if key == "file":
					try:
						f = open(value, 'rb')
						files = {key: f}
					except IOError:
						self.__createErrorObject(ErrorCode.IO_ERROR, "File not found")
						callback("", self.errorsList)
						return
				else:
					data.append((key, value))
		try:
			response = requests.post(queryStr, data=data, files=files, proxies=proxyDict, verify=False, timeout=600)
			if response.status_code != 200:
				jsonObj = json.loads(response.text)
				self.__parseHODResponse(jsonObj)
				callback("", self.errorsList)
			else:
				if async is False:
					resp = self.__parseHODResponse(response.json())
					if resp == "queued":
						callback("", self.errorsList)
					elif resp == "in progress":
						callback("", self.errorsList)
					elif resp == "errors":
						callback("", self.errorsList)
					else:
						callback(resp, None)
				else:
					jobID = self.__parseJobId(response)
					if jobID == "errors":
						callback("", self.errorsList)
					else:
						callback(jobID, None)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "Request timeout")
			callback("", self.errorsList)
		except requests.ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error")
			callback("", self.errorsList)

	def GetRequest(self, params, hodApp, async, callback):
		queryStr = self.hodEndPoint
		if async is True:
			queryStr += "async/%s/%s" % (hodApp, self.apiVersion)
		else:
			queryStr += "sync/%s/%s" % (hodApp, self.apiVersion)
		queryStr += "?apikey=%s" % (self.apiKey)
		for key, value in params.items():
			if key == "file":
				self.__createErrorObject(ErrorCode.INVALID_PARAM, "file resource must be uploaded with PostRequest function")
				callback("", self.errorsList)
				return
			if isinstance(value, list):
				for vv in value:
					queryStr += "&%s=%s" %(key, vv)
			else:
				queryStr += "&%s=%s" % (key, value)

		print queryStr
		try:
			response = requests.get(queryStr, verify=False, timeout=600)
			if response.status_code != 200:
				jsonObj = json.loads(response.text)
				print jsonObj
				self.__parseHODResponse(jsonObj)
				callback("", self.errorsList)
			else:
				if async is False:
					resp = self.__parseHODResponse(response.json())
					if resp == "queued":
						callback("", self.errorsList)
					elif resp == "in progress":
						callback("", self.errorsList)
					elif resp == "errors":
						callback("", self.errorsList)
					else:
						callback(resp, None)
				else:
					jobID = self.__parseJobId(response)
					if jobID == "errors":
						callback("", self.errorsList)
					else:
						callback(jobID, None)
		except requests.Timeout:
			self.__createErrorObject(ErrorCode.TIMEOUT, "Request timeout")
			callback ("", self.errorsList)
		except requests.ConnectionError:
			self.__createErrorObject(ErrorCode.CONNECTION_ERROR, "Connection error")
			callback ("", self.errorsList)

	def __createErrorObject(self,code, reason, detail=""):
		self.errorsList.resetErrorList()
		err = HODErrorObject()
		err.error = code
		err.reason = reason
		err.detail = detail
		self.errorsList.addError(err)

	def __parseHODResponse(self,jsonObj):
		self.errorsList.resetErrorList()
		if "actions" in jsonObj:
			actions = jsonObj["actions"]
			status = actions[0]["status"]
			if status == "queued":
				self.__createErrorObject(ErrorCode.QUEUED, "request is in queued")
				return "queued"
			elif status == "in progress":
				self.__createErrorObject(ErrorCode.IN_PROGRESS, "Request is in progress")
				return "in progress"
			elif status == "failed":
				print actions
				action = actions[0]
				errors = action["errors"]
				for error in errors:
					err = HODErrorObject()
					err.error = error["error"]
					err.reason = error["reason"]
					if "detail" in error:
						err.detail = error["detail"]
					self.errorsList.addError(err)
				return "errors"
			else:
				return actions[0]["result"]
		else:
			if "error" in jsonObj:
				err = HODErrorObject()
				err.error = jsonObj["error"]
				err.reason = jsonObj["reason"]
				if "detail" in jsonObj:
					err.detail = jsonObj["detail"]
				self.errorsList.addError(err)
				return "errors"
			else:
				return jsonObj

	def __parseJobId(self, response):
		jsonObj=response.json()
		if "error" in jsonObj:
				err = HODErrorObject()
				err.error = jsonObj["error"]
				err.reason = jsonObj["reason"]
				if "detail" in jsonObj:
					err.detail = jsonObj["detail"]
				self.errorsList.addError(err)
				return "errors"
		else:
			return jsonObj["jobID"]

class HODApps:
	RECOGNIZE_SPEECH = "recognizespeech"

	CANCEL_CONNECTOR_SCHEDULE = "cancelconnectorschedule"
	CONNECTOR_HISTORY = "connectorhistory"
	CONNECTOR_STATUS = "connectorstatus"
	CREATE_CONNECTOR = "createconnector"
	DELETE_CONNECTOR = "deleteconnector"
	RETRIEVE_CONFIG = "retrieveconfig"
	START_CONNECTOR = "startconnector"
	STOP_CONNECTOR = "stopconnector"
	UPDATE_CONNECTOR = "updateconnector"

	EXPAND_CONTAINER = "expandcontainer"
	STORE_OBJECT = "storeobject"
	EXTRACT_TEXT = "extracttext"
	VIEW_DOCUMENT = "viewdocument"

	OCR_DOCUMENT = "ocrdocument"
	RECOGNIZE_BARCODES = "recognizebarcodes"
	DETECT_FACES = "detectfaces"
	RECOGNIZE_IMAGES = "recognizeimages"

	GET_COMMON_NEIGHBORS = "getcommonneighbors"
	GET_NEIGHBORS = "getneighbors"
	GET_NODES = "getnodes"
	GET_SHORTEST_PATH = "getshortestpath"
	GET_SUB_GRAPH = "getsubgraph"
	SUGGEST_LINKS = "suggestlinks"
	SUMMARIZE_GRAPH = "summarizegraph"

	CREATE_CLASSIFICATION_OBJECTS = "createclassificationobjects"
	CREATE_POLICY_OBJECTS = "createpolicyobjects"
	DELETE_CLASSIFICATION_OBJECTS = "deleteclassificationobjects"
	DELETE_POLICY_OBJECTS = "deletepolicyobjects"
	RETRIEVE_CLASSIFICATION_OBJECTS = "retrieveclassificationobjects"
	RETRIEVE_POLICY_OBJECTS = "retrievepolicyobjects"
	UPDATE_CLASSIFICATION_OBJECTS = "updateclassificationobjects"
	UPDATE_POLICY_OBJECTS = "updatepolicyobjects"

	PREDICT = "predict"
	RECOMMEND = "recommend"
	TRAIN_PREDICTOR = "trainpredictor"

	CREATE_QUERY_PROFILE = "createqueryprofile"
	DELETE_QUERY_PROFILE = "deletequeryprofile"
	RETRIEVE_QUERY_PROFILE = "retrievequeryprofile"
	UPDATE_QUERY_PROFILE = "updatequeryprofile"

	FIND_RELATED_CONCEPTS = "findrelatedconcepts"
	FIND_SIMILAR = "findsimilar"
	GET_CONTENT = "getcontent"
	GET_PARAMETRIC_VALUES = "getparametricvalues"
	QUERY_TEXT_INDEX = "querytextindex"
	RETRIEVE_INDEX_FIELDS = "retrieveindexfields"

	CLASSIFY_DOCUMENT = "classifydocument"
	EXTRACT_CONCEPTS = "extractconcepts"
	CATEGORIZE_DOCUMENT = "categorizedocument"
	ENTITY_EXTRACTION = "extractentities"
	EXPAND_TERMS = "expandterms"
	HIGHLIGHT_TEXT = "highlighttext"
	IDENTIFY_LANGUAGE = "identifylanguage"
	ANALYZE_SENTIMENT = "analyzesentiment"
	TOKENIZE_TEXT = "tokenizetext"

	ADD_TO_TEXT_INDEX = "addtotextindex"
	CREATE_TEXT_INDEX = "createtextindex"
	DELETE_TEXT_INDEX = "deletetextindex"
	DELETE_FROM_TEXT_INDEX = "deletefromtextindex"
	INDEX_STATUS = "indexstatus"
	# public const string LIST_INDEXES = "listindexes" REMOVED
	LIST_RESOURCES = "listresources"
	RESTORE_TEXT_INDEX = "restoretextindex"