#!/usr/bin/env python

#  Remember to:
#    chmod 755 add_ticket.py
#  to make add_ticket.py executable.

#  We'll use the following (standard) Python libraries in
#  our script.

import sys
import http.client
import urllib
import json

#  Let's start by creating the HTTP request headers that
#  we need to talk to TDX through its API.

#  We're always going to send JSON when we talk to TDX, so let's
#  make that explicit by setting a "Content-type" HTTP header.

tdxHeaders = { 'Content-type': 'application/json' }

#  For almost every API request that we make, we
#  need to send TDX a "bearer" token (bearer tokens are
#  a standard way of dealing with a RESTful API
#  requiring authenticaiton). So before we can add a ticket,
#  we need to obtain a bearer token. We can use TDX's "auth"
#  API endpoint for that.

#  Okay here are our auth credentials (for UIC)
#  Replace with the credentials given to you.

tdxCredentials = {
  'username': 'your-id@uic.edu',
  'password': 'your-password'
}

#  Okay, let's encode our login credentials into a JSON string.

tdxLoginData = json.dumps(tdxCredentials)

#  Next, we setup the HTTPS connection. Note that this is HTTPS, so it's
#  safe to send our credentials since they'll be encrytped.

tdxConnection  = http.client.HTTPSConnection('help.uillinois.edu')

#  Okay, POST the authenticaiton request. Note that this request is
#  synchronous ... so the script won't continue until we get a response
#  back from TDX.

tdxConnection.request('POST', '/TDWebApi/api/auth', tdxLoginData, tdxHeaders)

#  Once we get a response, we'll check to see that it's
#  200 (i.e., "successful"). If not, we'll exit. Otherwise,
#  we'll read the response ... which is the bearer token.
#  In a production script, you would likely want to handle
#  errors much more gracefully.

tdxLoginResponse = tdxConnection.getresponse()
if tdxLoginResponse.status != 200:
  exit()
tdxBearerToken = tdxLoginResponse.read()

#  Because we'll always need to send the bearer token in an
#  "Authorization" HTTP header, let's add that to our set of headers.

tdxHeaders['Authorization'] = 'Bearer ' + tdxBearerToken

#  Okay, let's construct a ticket

#  In TDX, a ticket data structure has 111 "members". Of these,
#  25 are "editable" ... and 6 are "required". Here is a
#  comprehensive list of editable and requried ticket members:

#  title:              editable, required
#  details:            editable
#  typeID:             editable, required
#  formID:             editable
#  accountID:          editable, required
#  sourceID:           editable
#  statusID:           editable, required
#  impactID:           editable
#  urgencyID:          editable
#  priorityID:         editable, required
#  goesOffHoldDate:    editable
#  requestorUID:       editable, required
#  estimatedMinutes:   editable
#  startDate:          editable
#  endDate:            editable
#  responsibleUID:     editable
#  responsibleGroupID: editable
#  timeBudget:         editable
#  expensesBudget:     editable
#  locationID:         editable
#  locationRoomID:     editable
#  serviceID:          editable
#  articleID:          editable
#  articleShortcutID:  editable
#  attributes:         editable

#  Let's just focus on creating a minimal ticket with a title, a description, and
#  the remaining required members.

#  Okay, ticket title and ticket description are simple enough:

title = raw_input("Enter a title: ") 
description = raw_input("Enter description: ")

#  Now, let's look at typeID, statusID, and priorityID.
#  As you likely guessed, these are for ticket type, status
#  and priority. Problem is that TDX wants iteger IDs for
#  these things ... and we do not know what these integer IDs
#  are. Luckily, we have APIs that will tell us.

#  Let's start with ticket statuses. We'll call the "status" endpoint to get
#  those. Note the "31" in the API endpoint request ... that is the "ticket
#  app ID". There is a separate API endpoint that will list all
#  the apps (and their IDs) that we can access. For UIC, all tickets
#  are part of "app 31", so we'll stick with that.

tdxConnection.request('GET', '/TDWebApi/api/31/tickets/statuses', "", tdxHeaders)
tdxResponse = tdxConnection.getresponse()

#  If the HTTP response isn't 200, we'll
#  exit, just like we did before.

if tdxResponse.status != 200:
  exit()

#  Now we'll decode the response we got from TDX as a UTF-8
#  string. We'll simply ignore any UTF-8 encoding errors ... in
#  a production script, you would likely want to handle things
#  more gracefully.

tdxData = tdxResponse.read().decode('utf-8', errors="ignore")

#  Next, we'll ask that Python read the string as JSON data
#  and store it in a Python array.

ticketStatuses = json.loads(tdxData)

#  Finally, we'll print out the status IDs and their names.

for ticketStatus in ticketStatuses:
  print(str(ticketStatus['ID']) + ": " + ticketStatus['Name'])

#  And ask the end-user to pick one of those IDs.

statusID = int(raw_input("Pick a ticket status ID number: "))

#  Okay, now that we've got statuses down, let's do the same for ticket
#  priorities:

tdxConnection.request('GET', '/TDWebApi/api/31/tickets/priorities', "", tdxHeaders)
tdxResponse = tdxConnection.getresponse()
if tdxResponse.status != 200:
  exit()
tdxData = tdxResponse.read().decode('utf-8', errors="ignore")
ticketPriorities = json.loads(tdxData)
for ticketPriority in ticketPriorities:
  print(str(ticketPriority['ID']) + ": " + ticketPriority['Name'])
priorityID = int(raw_input("Pick a ticket priority ID number: "))

#  And then, ticket types:

tdxConnection.request('GET', '/TDWebApi/api/31/tickets/types', "", tdxHeaders)
tdxResponse = tdxConnection.getresponse()
if tdxResponse.status != 200:
  exit()
tdxData = tdxResponse.read().decode('utf-8', errors="ignore")
ticketTypes = json.loads(tdxData)
for ticketType in ticketTypes:
  print(str(ticketType['ID']) + ": " + ticketType['Name'])
typeID = int(raw_input("Pick a ticket type ID number: "))

#  Okay, now let's tackle AccountID. In TDX, AccountID roughly translates
#  to "department" or some other group-y thing within our TDX isntance (e.g.
#  "UIC Students"). Again, TDX offers an API that would let us look this up ...
#  but since all tickets we create here will have the same AccountID (the ID
#  for UIC Technology Services), we'll just go with it ... 5475 = "Technology Servies".

accountID = 5475

#  Finally, we need a requestorUID. In TDX, UIDs are UUIDs. So we'll need to look
#  that up based on NetID. Again, there is an API just for this. First, let's
#  ask the end user to tell us who we need to look for:

requestorNetID = raw_input("Enter the NetID for the ticket requestor: ")

#  Now, we'll construct the search record:

requestorSearch = requestorNetID + "@uic.edu"

#  ... and send it to TDX. Notice that this time, we're sending the search
#  as a URL query string:

tdxConnection.request('GET', '/TDWebApi/api/people/lookup' +
  "?searchText=" + requestorSearch, "", tdxHeaders)

#  Again, we'll read the response from TDX and decode it:

tdxResponse = tdxConnection.getresponse()
if tdxResponse.status != 200:
  print(tdxResponse.status)
  exit()
tdxData = tdxResponse.read().decode('utf-8', errors="ignore")
tdxUser = json.loads(tdxData)

#  The requestorUID will be the search target's UID. Note that the "people search"
#  API endpoint returns an array of possible matches. Since we know that only one
#  person can be associated with a NetID, we'll open the only item (zeroth) of the 
#  array.

requestorUID = tdxUser[0]['UID']

#  At last, we have everything we need. We can now create a ticket request!

#  Let's begin by creating the ticket data structure:

ticket = {
  'Title': title,
  'Description': description,
  'StatusID': statusID,
  'PriorityID': priorityID,
  'TypeID': typeID,
  'AccountID': accountID,
  'RequestorUid': requestorUID
}

#  At last, the moment has come. Let's post the ticket to TDX. Notice that this
#  time, we're looking for a HTTP 201 ("added") response back from TDX.

tdxTicketData = json.dumps(ticket)

tdxConnection.request('POST', '/TDWebApi/api/31/tickets', tdxTicketData, tdxHeaders)
if tdxResponse.status != 201:
  print("Ticket not added")
  exit()
else:
  print("Ticket added")

#  Just for fun, let's print out the new ticket's details:

tdxData = tdxResponse.read().decode('utf-8', errors="ignore")
tdxNewTicket = json.loads(tdxData)

print(tdxNewTicket)
