import ConnectionHandler
import requests
import json


def Comparison(access):
	azuretables = ConnectionHandler.createtable()
	
	resourcegroup = ConnectionHandler.resources()
	resourcegroupname = ConnectionHandler.resourcegroupobject()
	r1 = requests.get(resourcegroup, headers= {"Authorization" : 'bearer {}'.format(access)})
	r2 = requests.get(resourcegroupname, headers= {"Authorization" : 'bearer {}'.format(access)})
	jsonresponse1 = json.loads(r1.text)
	jsonresponse2 = json.loads(r2.text)
	if r1.status_code == 401:
		return(0)

	rgdict = []
	rgdict2 = []
	try:
		for value in jsonresponse1['value']:

			rgdict.append(value)
	except Exception as e:
		if str(e) == "'value'":
			print("No Resource Group Available")
			
	for id in rgdict:
		Pkey = id['name']
		RKey = jsonresponse2['name']
		Types = id['type']
		Location = id['location']
		identif = id['id']
		check = ConnectionHandler.CheckIDs(Pkey,RKey)
		rgdict2.append(identif)
		
		if check == None:
			ConnectionHandler.storageaccounthandler(Pkey,RKey,Types,Location, identif)
			ConnectionHandler.TeamsConnection("New Resource created: \n\n" + "**Name:** " + Pkey + "\n\n" + "**Resource Group:** " + RKey + "\n\n" + "**Resource Type:** " + Types + "\n\n" + "**Resource ID:** " + identif + "\n\n" + "**Location:** " + Location)

		
		
	Backstate = ConnectionHandler.CheckforDeleted()
	diffcheck = [item for item in Backstate if item not in rgdict2]
	if len(diffcheck) != 0:
		deletion = ConnectionHandler.DeleteEntity(diffcheck)
		print(deletion)

	else:
		print("No orphaned resources")

def AZConnect():
	global tokens
	tokens = ConnectionHandler.AzureConnection()
	return(tokens)

if __name__ == "__main__":
	
	status = 1
	 
	while status:
		# This is when I get the token wastefully
		azconnection = AZConnect()
		tokencheck = ConnectionHandler.TokenCheck(azconnection)
		if tokencheck == "Invalid":
			
			azconnection = AZConnect()

		else:
			Comparison(azconnection)
			continue
