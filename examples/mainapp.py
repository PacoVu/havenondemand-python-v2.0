from Tkinter import *
import Tkinter
import time
import ttk

import sys
sys.path.append('../havenondemand')

from hodclient import *

class simpleapp_tk(Tkinter.Tk):

	hodApp = ""
	jobID = ""
	client = None
	source = "text"
	Lb1 = None

	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()
		self.client = HODClient("your-apikey")

	def initialize(self):
		self.grid()

		self.box_value = StringVar()
		self.box = ttk.Combobox(self.parent,textvariable=self.box_value)
		self.box.bind("<<ComboboxSelected>>", self.newselection)
		self.box['values'] = ('text', 'file', 'reference', 'url', 'json')
		self.box.current(3)
		self.box.grid(column=0, row=0,sticky='W')

		self.apis_value = StringVar()
		self.apis = ttk.Combobox(self.parent,textvariable=self.apis_value)
		self.apis['values'] = (HODApps.ANALYZE_SENTIMENT, HODApps.ENTITY_EXTRACTION, HODApps.EXTRACT_CONCEPTS, HODApps.OCR_DOCUMENT, HODApps.RECOGNIZE_SPEECH, HODApps.RECOGNIZE_BARCODES, HODApps.RECOGNIZE_IMAGES)
		self.apis.current(0)
		self.apis.grid(column=1, row=0,sticky='W')

		self.reqmode_value = StringVar()
		self.reqmode = ttk.Combobox(self.parent,textvariable=self.reqmode_value)

		self.reqmode['values'] = ('sync', 'async')
		self.reqmode.current(0)
		self.reqmode.grid(column=2, row=0,sticky='W')

		self.reqmethod_value = StringVar()
		self.reqmethod = ttk.Combobox(self.parent,textvariable=self.reqmethod_value)
		self.reqmethod['values'] = ('get', 'post')
		self.reqmethod.current(0)
		self.reqmethod.grid(column=3, row=0,sticky='W')

		self.entryVariable = Tkinter.StringVar()
		self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
		self.entry.grid(column=0,row=1,columnspan=3,sticky='EW')
		self.entry.bind("<Return>", self.OnPressEnter)
		self.entryVariable.set(u"http://www.cnn.com")

		hint = Tkinter.Label(self,text="(use ## to separate multiple inputs)",anchor="e",font=("Helvetica", 10),justify=LEFT)
		hint.grid(column=3,row=1,sticky='W')
		#self.labelVariable.set(u"Use ##|## to separate multiple inputs")

		button = Tkinter.Button(self,text=u"Submit",command=self.OnButtonClick)
		button.grid(column=4,row=1)
		self.labelVariable = Tkinter.StringVar()

		label = Tkinter.Label(self,textvariable=self.labelVariable,anchor="e",fg="blue",font=("Helvetica", 12),justify=LEFT)
		label.grid(column=0,row=2,columnspan=4,sticky='W')
		self.labelVariable.set(u"Hello Haven OnDemand APIs!")

		self.grid_columnconfigure(0,weight=1)

		self.resizable(True,True)

	def newselection(self, event):
		self.source = self.box.get()

	def immediately(self):
		print self.Lb1.curselection()

	def OnButtonClick(self):
		if self.jobID == "":
			self.GetTextAndSendRequest(self.entryVariable.get())
		else:
			print self.jobID
			self.labelVariable.set("Sending getJobResult %s. Please wait..." % (self.jobID))
			self.client.GetJobResult(self.jobID, self.requestCompletedWithContent)

	def OnPressEnter(self,event):
		if self.jobID == "":
			self.GetTextAndSendRequest(self.entryVariable.get())
		else:
			print self.jobID
			self.labelVariable.set("Sending getJobResult %s. Please wait..." % (self.jobID))
			self.client.GetJobResult(self.jobID, self.requestCompletedWithContent)

	def GetTextAndSendRequest(self,text):
		self.hodApp = self.apis.get()
		self.source = self.box.get()
		srcs = text.split("##")
		src = []
		for item in srcs:
			src.append(item)
		params = {}
		params[self.source] = src
		if self.hodApp == HODApps.ANALYZE_SENTIMENT:
			params["language"] = "eng"
		elif self.hodApp == HODApps.ENTITY_EXTRACTION:
			params["entity_type"] = ["places_eng","people_eng","companies_eng"]
			params["unique_entities"] = "true"
		elif self.hodApp == HODApps.RECOGNIZE_SPEECH:
			params["interval"] = "20000"

		mode = self.reqmode.get()
		method = self.reqmethod.get()
		self.labelVariable.set("Sending request. Please wait...")
		time.sleep(2)
		if method == "get":
			print "call get"
			if mode == "sync":
				self.client.GetRequest(params,self.hodApp,async=False,callback=self.requestCompletedWithContent)
			else:
				self.client.GetRequest(params,self.hodApp,async=True,callback=self.requestCompletedWithJobId)
		else:
			print "call post"
			if mode == "sync":
				self.client.PostRequest(params,self.hodApp,async=False,callback=self.requestCompletedWithContent)
			else:
				self.client.PostRequest(params,self.hodApp,async=True,callback=self.requestCompletedWithJobId)

	def requestCompletedWithJobId(self,response, error):
		if error != None:
			for err in error.errors:
				print "code: %d" % (err.error)
				result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
				self.labelVariable.set(result)
		else:
			self.jobID = response
			self.labelVariable.set("jobID is ready. " + self.jobID)
			self.client.GetJobResult(self.jobID, self.requestCompletedWithContent)

	def requestCompletedWithContent(self,response,error):
		result = ""
		if error != None:
			for err in error.errors:
				result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error,err.reason, err.detail)
		else:
			if self.hodApp == 'ocrdocument':
				texts = response["text_block"]
				for text in texts:
					result += "Recogmized text: " + text["text"]
					result += "\n"
			elif self.hodApp == "extractentities":
				entities = response["entities"]
				for entity in entities:
					print entity["type"]
					if entity["type"] == "companies_eng":
						result += "Company name: " + entity["normalized_text"] + "\n"
					elif entity["type"] == "places_eng":
						result += "Place name: " + entity["normalized_text"] + "\n"
					else:
						result += "People name: " + entity["normalized_text"] + "\n"
			elif self.hodApp == "analyzesentiment":
				positives = response["positive"]
				for pos in positives:
					result += "Sentiment: " + pos["sentiment"] + "\n"
					if pos.get('topic'):
						result += "Topic: " + pos["topic"] + "\n"
					result += "Score: " + "%f " % (pos["score"]) + "\n"
					if pos.get('documentIndex'):
						result += "Doc: " + str(pos["documentIndex"]) + "\n"
				negatives = response["negative"]
				for neg in negatives:
					result += "Sentiment: " + neg["sentiment"] + "\n"
					if neg.get('topic'):
						result += "Topic: " + neg["topic"] + "\n"
					result += "Score: " + "%f " % (neg["score"]) + "\n"
					if neg.get('documentIndex'):
						result += "Doc: " + str(neg["documentIndex"]) + "\n"
			elif self.hodApp == "recognizespeech":
				documents = response["document"]
				for doc in documents:
					result += doc["content"] + "\n"
					if "offset" in doc["offset"]:
						result += "%d" % (doc["offset"]) + "\n"
			elif self.hodApp == HODApps.EXTRACT_CONCEPTS:
				concepts = response["concepts"]
				for concept in concepts:
					result += concept["concept"] + "\n"
					result += "%d" % (concept["occurrences"]) + "\n"
			else:
				result = "empty response"
			self.jobID = ""

		self.labelVariable.set(result)

if __name__ == "__main__":
	app = simpleapp_tk(None)
	app.title('Python HODClient Demo')
	app.geometry('{}x{}'.format(800, 600))

	app.mainloop()