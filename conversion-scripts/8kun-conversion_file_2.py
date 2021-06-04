import json
import os

#===============================================================================
#                 Conversion Script 2: Create 8Kun Master JSON File
#                       1. Remove Duplicate Threads
#                       2. Consolidate all thread comments from all scrapes 
#===============================================================================

#===============================================================================
#                                   Setup
#===============================================================================

### This file contains a list of all thread objects. It contains duplicates, each thread appears e.g. 30 times but in each case that thread may have a unique comment not found in other threads. 
cleanedDataFilePath = "data/8kun-scraped-threads-all.json"

with open(cleanedDataFilePath, 'r') as file:
    json_data = file.read()

    ### threadList - List of thread objects loaded from JSON file of converted HTML. Contains duplicates
    threadList = json.loads(json_data)

### threadCommentsDict:
# key: threadId
# value: commentsDict
## commentsDict
# key: commentId
# value: commentObject 
threadCommentsDict = {}

### threadObjectsDict:
# key: threadId
# value: threadObject # NOTE: threadObject is simply the first thread object found in the scraped file
threadObjectsDict = {}

#===============================================================================
#                          Collect Unique Threads
#===============================================================================

for thread in threadList:
    ### If threadId not yet encountered, create new key
    if thread['thread_Id'] not in threadCommentsDict.keys():
        threadCommentsDict[thread['thread_Id']] = {} ### here we will have a dict of comment objects
    
    ### If threadId not yet encountered, create new key
    if thread['thread_Id'] not in threadObjectsDict.keys():
        threadObjectsDict[thread['thread_Id']] = thread

    ### If threadId has just been created, this will be an empty object, otherwise, it already will contain some comments
    commentsDict = threadCommentsDict[thread['thread_Id']]
    
    ### For each comment in the current thread, check if we have already encoutered this comment under this thread, if not, store it in our comments Dict
    for comment in thread['comments']:
        if comment['comment_Id'] not in commentsDict.keys():
            commentsDict[comment['comment_Id']] = comment


#===============================================================================
#                          Create Master and Sample Thread List
#===============================================================================

### Simple helper method
def commentsDictToList(commentsDict):
    commentsList = [] 
    for commentObject in commentsDict.values(): 
        commentsList.append(commentObject) 
    return commentsList

### From threadCommentsDict which is unique, take each thread and retrieve the entire object
masterThreadList = []
for threadId in threadCommentsDict.keys():
    threadObject = threadObjectsDict[threadId] # get full object from threadList  
    threadObject['comments'] = commentsDictToList(threadCommentsDict[threadId]) # get full comments list from commentsDict
    masterThreadList.append(threadObject)

### Create "sub-list" of 3 threads, to store as sample file
sampleCounter = 0   
eightKunThreadSamples = []
for thread in masterThreadList:
    if sampleCounter < 3:
        eightKunThreadSamples.append(thread)
    sampleCounter += 1

#===============================================================================
#                     Write to File
#                      - 1x Master file with ALL Threads
#                      - 1x Sample file with 3 Threads for human manual review
#===============================================================================

### Write Master file
with open("data/8kun-unique-threads-all.json", 'w') as f:
    json.dump(masterThreadList, f)

### Write Sample File
with open("data/8kun-unique-threads-sample.json", 'w') as f:
    json.dump(eightKunThreadSamples, f)
