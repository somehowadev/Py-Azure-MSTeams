PyAzureMSTeams
======

## Overview

I created this to deal with sending notifications about my Azure resources to my Microsoft Teams channel.

I designed it with the idea that monitoring should only be done for individual resources, within a specific resource group. If you've got entire resource groups in production disappearing you've got bigger problems my friend.  
It's possible to watch entire subscriptions if you'd like and observe the resource groups themselves but personally I didn't have a use for that. Especially since I might just be testing new resources/stuff and don't need to be notified about it.
The program uses an Azure storage account to keep state within it's tables. 

## Useage

```
python PyAzureMSTeams.py 

```

## Running inside a WebApp

To run it inside a web app as a continuous job, install Python 3.6+ on the App service plan. Create a .zip archive of this repository and upload it as a continuous web job. It should download the required libraries on each load. 

Though this application doesn't store anything locally and can deal with restarts/etc, better to keep it somewhere long running.

## Prerequisites

You'll need to create an Azure Storage Account first. It can be either version 1 or 2.

#### Storage Account: 

Access Tier: Hot

Performance: Standard

Replication: (No requirement here, I'd recommend LRS for cost reasons)

Other options can be changed as desired. 

The program will try to create a table when it first starts/soft fails if the table exists.

### Azure AD Application Registration

Application Type: Web App/API

You'll need to register an application in Azure AD for retrieving tokens.
The application does _not_ need access to any APIs.
Generate a client_secret and make a note of the application ID/Client Secret.

### Access Control (IAM)

You'll need to give the reader permission to the application we've just registered.
Pick the resource group you'd like notifications on (this is more suited for just sitting on the Prod resource group rather than a test environment where things are constantly changing!)
This was designed with the idea that it'll always be 1 - 1, so the program only watches 1 RG. I might improve this on later.

 
### Microsoft Teams Webhook 

We'll need to create a incoming webhook in MS Teams.


1. Decide on the team you want the webhook to reside in (or create a new team)
2. Click on the Store within Microsoft Teams.
3. Search for "Incoming Webhook" within the store and select the app.
4. Choose the team you'd like to add it to and install it.
5. Pick the channel you want to add it to and setup the connector (if it's a brand new team, it's probably going to be "General")
6. Name the incoming webhook and give it an appropiate image. 
7. Click Create
8. A webhook url would have been generated for you, make a note of it.



### Config.json

Now we'll create a config.json file in the directory that contains the program. There's a dummy one included in the repo.

The format following:

```
{
	"AzureApp":
		{
		"Client_ID": "X",
		"Client_Secret": "X",
		"scope": "https://management.azure.com/.default",
		"tenant": "X",
		"grant_type": "client_credentials"
		},
	"AzureResources":
		{
		"resourcegroupresources": "https://management.azure.com/subscriptions/"SubscriptionID"/"ResourceGroupName"/resources?api-version-2017-05-10",
		"resourcegroup": "https://management.azure.com/subscriptions/"SubscriptionID"/"ResourceGroupName"?api-version-2017-05-10"" 
		},	
	"AzureStorage":
		{
		"Account_Name": "X",
		"Key": "X",
		"Name": "KnownState"
		},
	"TeamsWebhook":
		{
		"URL":"X"
		}
}
```

# Done! 

Just run the program.

## Quirks

1. Personally didn't use the ADAL library, since the client credential flow is easy enough. 

2. The program is surprisingly quick, you'll notice it'll notify you before the Azure portal does. 

3. On each run, it requests a new bearer token. Yes, it's wasteful and is not intended. Making me slightly regret staying away from ADAL actually.
This is due to the fact that I have no way of updating the variable that contains the bearer token _outside_ of the while loop. I've tried a few workarounds but for the most part, the token handling needs to be looked at again.
I'm sure I've missing something so if anyone has any ideas, I'd appreciate it. I only really had a day's worth of effort to put into this and I figured wasteful but working is still slightly better than not working at all.

4. I'll have a look at this again soon.


5. The 1 - 1 mapping, I made this based on my own environment, where we don't have many resource groups, one of which is prod and we focus on placing all prod stuff in that resource group. Your setup might be different and thus might need multiple instances to cover your environment, I'll also make the argument that it's objectively better to not have many resource groups and to segment by environment.

6. Resource names shouldn't have a backslash in them or any other characters that don't comply with Azure Storage tables. (Can look into this, I think the restriction is just based on the partition/row key).


## Tips 

Run this on an App Service Plan as a continuous web job, including a batch file to download everything in the requirements.txt (since you're not guaranteed to stay on the same infrastructure)

Download the MS Teams app and follow the channel (right click on channel -> follow)  to get notifications.

## To DO

1. Fix token handling (probably rework it)
2. Offer option to do 1 - many rather than 1.1
3. Support for running multipe instances at the same time for some simple failover scenarios.

