import os
import pygsheets
import numpy as np
from dotenv import load_dotenv
from discordInfo import users
from datetime import datetime
from colorama import Back, Fore, Style

#   Load Environment Variables
load_dotenv()
credentialsPath = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
#sheetID = os.getenv('TEST_GOOGLE_SHEET')    #test
sheetID = os.getenv('PROD_GOOGLE_SHEET')   #real

gc = pygsheets.authorize(service_account_file=credentialsPath)
sh = gc.open_by_key(sheetID)
wks = sh[0]


paidHeaderLocation = ((4, 8), (4, 13))      #locations of "X paid Y" headers
paidHeaders = wks.get_values(paidHeaderLocation[0], paidHeaderLocation[1])[0]



def checkMoney():
    lines = []
    lines.append(wks.get_value("H1"))
    lines.append(wks.get_value("J1"))
    lines.append(wks.get_value("L1"))

    for i in range(len(lines)):
        if "owes" in lines[i]:
            # @ the person who owes money
            lines[i] = f"@" + lines[i][0].lower() + lines[i][1:]
    
    return "\n".join(lines)




def paid(authorID, userID, amount):   
    #get all the data together
    receiving = getAuthor(userID).capitalize()
    sending = getAuthor(authorID).capitalize()

    # find where we're supposed to put it
    paidString = f"{sending} paid {receiving}"
    print(paidHeaders)
    paidIndex = paidHeaders.index(paidString) + paidHeaderLocation[0][1]
    
    (x, y) = findOpenSpace((paidHeaderLocation[0][0]+1, paidIndex))
    
    # Now add the data to the sheet
    #wks.update_value((rowNum, paidIndex), amount)
    wks.update_value((x, y), amount)
    
    # @ the person who was paid
    return f"Success! {sending} sent @{receiving.lower()} ${amount:.2f}"                
            



def bill(authorID, split, amount, description):
    #check to see if it's in the right format
    # /bill [3 / 4] [amount] [multiple word description]
        
    # gather the relevant info
    sender = getAuthor(authorID)[0].upper()
    date = datetime.now().strftime("%m/%d/%y")
    if split == 3: split = "JNI"
    if split == 5: split = "JNLIM"
    
    #find where to put it
    (x, y) = findOpenSpace((2, 1))
    
    #now add the data to the sheet
    wks.update_values(crange=(x, y), values=[[date, sender, description, amount, split]])
    
    # @ other users who did not pay for the bill
    response = ""
    for name in users.keys():
        if name != getAuthor(authorID):
            response += f"@{name} "
    
    response += f"Success! {getAuthor(authorID).capitalize()} paid ${amount:.2f} for {description}. The people paying for this are: {split}"
    return response
    


def splitBill(authorID, userID, amount, description):
    if authorID == userID:
        return "Why would you split something with yourself lol"
    author = getAuthor(authorID)
    user = getAuthor(userID)
    split = author[0].upper() + user[0].upper()
    response = bill(authorID, split, amount, description)
    return f"Success! {getAuthor(authorID).capitalize()} paid ${amount:.2f} for {description}, which he is splitting with @{getAuthor(userID).lower()}"



def charge(authorID, userID, amount, description):
    if authorID == userID:
        return "Why would you charge yourself lol"
    user = getAuthor(userID)
    split = user[0].upper()
    response = bill(authorID, split, amount, description)
    return f"Success! {getAuthor(authorID).capitalize()} charged @{getAuthor(userID).lower()} ${amount:.2f} for {description}"




def getAuthor(author):
    strAuthor = list(users.keys())[list(users.values()).index(author)]
    if strAuthor == "lauren":
        strAuthor = "nico"
    return strAuthor
    
    
def findOpenSpace(coords):    
    #takes in a cell in the spreadsheet
    #returns the first cell UNDER that cell that does not have data in it
    (x, y) = coords
    
    i = 0
    while True:     #probably the wrong way to find the first unused spot
        workspace = wks.get_values((x+(i*100), y), (x+((i+1)*100), y))
        if len(workspace) == 101:
            i+=1
        else:
            firstUnusedX = len(workspace) + x + (i*100)
            break
        
    return (firstUnusedX, y)
    
    
    