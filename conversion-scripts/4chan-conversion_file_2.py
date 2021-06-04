import json
import os

#===============================================================================
#                 Conversion Script 2: Create 4Chan Master JSON File
#                       1. Remove Duplicate Threads
#                       2. Consolidate all thread comments from all scrapes 
#===============================================================================

#===============================================================================
#                                   Setup
#===============================================================================

### This file contains a list of all thread objects. It contains duplicates, each thread appears e.g. 30 times but in each case that thread may have a unique comment not found in other threads. 
fourchanData = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/"
dataPath = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/2020-06/"

threadIds = []
commentIds = []

threadObjects = {}
commentObjectsPerThread = {}

### Get sub directories and files scraped
subdirs = [x[0] for x in os.walk(fourchanData)]
subdirs.pop(0) # we must remove the first entry as it is this directory itself

#===============================================================================
#                          Collect Unique Threads
#===============================================================================

for subdir in subdirs: ### For each sub directory
    for fn in os.listdir(subdir): ### For each File in a sub directory
            fullFilePath = os.path.join(subdir, fn) ### Set file path

            ### Open the file
            with open(fullFilePath, 'r') as data_file:
                json_data = data_file.read()
            if not len(json_data) > 0: ### If the size of the data is not greater than 0, there is no data, do not open
                pass
            else:
                data = json.loads(json_data)    

                for page in data: ### For each page in the 4Chan JSON file
                    for  thread in page['threads']:  ### For each Thread in the page
                        if 'id' in thread.keys(): 
                            
                            ### Here we store the ThreadId in an IdList and we store the ThreadObject in a Dict
                            threadIds.append(thread['id'])
                            threadObjects[thread['id']] = thread

                        ### If this thread has last replies, iterate through each comment, add the comment id to an ID List.
                        ### If this thread ID has not been already inserted into our ThreadIDComment Dict, we create a new list at this entry
                        ### and we add this comment object to that Thread Id 
                        if 'last_replies' in thread.keys():
                            for comment in thread['last_replies']:
                                if 'id' in comment.keys(): 
                                    commentIds.append(comment['id'])
                                    if 'id' in thread.keys(): 
                                        if not thread['id'] in commentObjectsPerThread.keys():                                        
                                            commentObjectsPerThread[thread['id']] = []
                                        commentObjectsPerThread[thread['id']].append(comment)
                data_file.close()
    
    ### After collecting all comment and thread objects, we combine them into one JSON
    fullThreads = []

    for threadId in threadObjects:

        ### 
        currentThread = threadObjects[threadId]
        ### IFF this thread has comments in the comments object, add them to the thread object
        if threadId in commentObjectsPerThread.keys(): 
                currentThread['num_scraped_comments'] = len(commentObjectsPerThread[threadId])
                currentThread['scraped_comments'] = commentObjectsPerThread[threadId]
        fullThreads.append(currentThread)

#===============================================================================
#                          Create Master and Sample Thread List
#===============================================================================

sameplFullThreads = []
for index in range(1,11):
    sameplFullThreads.append(fullThreads[index])

#===============================================================================
#                     Write to File
#                      - 1x Master file with ALL Threads
#                      - 1x Sample file with 3 Threads for human manual review
#===============================================================================

### Write Master file
with open("data/4chan-unique-threads-all.json", 'w') as f:
    json.dump(fullThreads, f)

### Write Sample File
with open("data/4chan-unique-threads-sample.json", 'w') as f:
    json.dump(sameplFullThreads, f)