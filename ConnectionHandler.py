import json 
import ConnectionHandler
import datetime
import azure
import requests
import jwt
import time
from azure.cosmosdb.table.tableservice import TableService

def AzureConnection():

	# Since we're simply using the client credential flow, we can do the authentication ourselves
	# All that's involved is a HTTP POST to the token endpoint for Azure AD and we get a bearer token.
	# There is no real requirement to avoid ADAL, I just like doing it myself :) 

	#Example config.json
	#{'AzureApp': {'Client_ID': 'X', 'Client_Secret': 'X', 'scope': 'https://graph.windows.net/.default', 'tenant': 'contoso.com'}}

	with open('config.json', 'r') as f:
		config = json.load(f)
	connectdiction = {}
	connectdiction.update(config['AzureApp'])
	authrequest = requests.post("https://login.microsoftonline.com/" + config['AzureApp']['tenant'] + "/oauth2/v2.0/token",data=connectdiction)
	bearers = authrequest.text
	jsonbearer = json.loads(bearers)
	return(jsonbearer['access_token'])


def TokenCheck(passedtoken):
	decoded = jwt.decode(passedtoken,"", False, algorithms=['RS256'])
	tokenexpir = datetime.datetime.fromtimestamp(decoded['exp']).timestamp()
	currenttime = datetime.datetime.now().timestamp()
	strippedtimestamp = (str(currenttime).split(".")[0])
	tokenexpired = (str(tokenexpir).split(".")[0])
	if tokenexpired == strippedtimestamp:
		return("Invalid")
		# aka they match, token now invalid
	else:
		print(tokenexpired)
		print(strippedtimestamp)
		return("Valid")

def resources():
	#	{
	#"AzureResources":
	#	{
	#	"resourcegroupresources": "URI to resources inside resource group",
	#	"resourcegroup": "URI to resource group itself"
	#	}
	#}	
	with open("config.json", "r") as u:
		resourcegroup = json.load(u)

	return(resourcegroup['AzureResources']['resourcegroupresources'])

def resourcegroupobject():
	with open("config.json", "r") as u:
		resourcegroupname = json.load(u)

	return(resourcegroupname['AzureResources']['resourcegroup'])


def storageaccounthandler(partitionkey, rowkey, type, location, identif ):
	#PartitionKey = Resource Name (Resource ID is too long/contains slashes - violates Azure naming rules)
	#Rowkey = Resource Group Name

	with open("config.json", "r") as s:
		saccount = json.load(s)
	accountname = saccount['AzureStorage']['Account_Name']
	accountkey = saccount['AzureStorage']['Key']
	table_service = TableService(account_name=accountname, account_key=accountkey)
	tablename = saccount['AzureStorage']['Name']
	task = {'PartitionKey': partitionkey, 'RowKey': rowkey, 'Type' : type, 'Location' : location, 'ID' : identif}
	
	if table_service.exists(tablename,timeout = None):
		print("Table up")
	else:
		createtable()
	try:
		insertions = table_service.insert_entity(tablename,task)

	except Exception as AzureConflictHttpError:

		return()

def CheckIDs(partitionkey, rowkey):
	with open("config.json", "r") as s:
		saccount = json.load(s)
	accountname = saccount['AzureStorage']['Account_Name']
	accountkey = saccount['AzureStorage']['Key']
	table_service = TableService(account_name=accountname, account_key=accountkey)
	tablename = saccount['AzureStorage']['Name']

	try:
		tasks = table_service.get_entity(tablename,partitionkey,rowkey)
		return(tasks)
	
	except:
		print("Exception")
	

def createtable():
	with open("config.json", "r") as s:
		saccount = json.load(s)
	accountname = saccount['AzureStorage']['Account_Name']
	accountkey = saccount['AzureStorage']['Key']
	table_service = TableService(account_name=accountname, account_key=accountkey)
	tablename = saccount['AzureStorage']['Name']

	table_service.create_table(tablename)


def TeamsConnection(Message):
	with open("config.json", "r") as t:
		teamsjson = json.load(t)
	teamsuri = teamsjson['TeamsWebhook']['URL']
	r3 = requests.post(teamsuri, json={"Text": Message})
	r3.raise_for_status()
	if r3.status_code == 409:
		# Rate limit 
		time.sleep(10)
		r3 = requests.post(teamsuri, json={"Text": Message})
	return()

def CheckforDeleted():
	with open("config.json", "r") as s:
		saccount = json.load(s)
	accountname = saccount['AzureStorage']['Account_Name']
	accountkey = saccount['AzureStorage']['Key']
	table_service = TableService(account_name=accountname, account_key=accountkey)
	tablename = saccount['AzureStorage']['Name']

	results = table_service.query_entities(tablename, filter = None)
	resultlist = []
	for result in results:
		resultlist.append(result['ID'])
	return(resultlist)

def DeleteEntity(ids):
	with open("config.json", "r") as s:
		saccount = json.load(s)
	accountname = saccount['AzureStorage']['Account_Name']
	accountkey = saccount['AzureStorage']['Key']
	table_service = TableService(account_name=accountname, account_key=accountkey)
	tablename = saccount['AzureStorage']['Name']

	for item in ids:
			tasks = table_service.query_entities(tablename, filter="ID eq '{}'".format(item))
			for task in tasks:
				dic = {"PartitionKey" : task.PartitionKey, "RowKey" : task.RowKey, "ID" : item, "Location" : task.Location, "Type" : task.Type}
				ConnectionHandler.TeamsConnection("**Resource** **Deleted**: \n\n" + "**Name:** " + dic["PartitionKey"] + "\n\n" + "**Resource Group:** " + dic["RowKey"] + "\n\n" + "**Resource Type:** " + dic["Type"] + "\n\n" + "**Resource ID:** " + dic["ID"] + "\n\n" + "**Location:** " + dic["Location"])
				deletentry = table_service.delete_entity(tablename, task.PartitionKey, task.RowKey)
	return()