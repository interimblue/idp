import requests
import urllib.request
import re
import logging
import json
import os
import datetime as dt
import sys
import time
import signal
from bs4 import BeautifulSoup

#===============================================================================
#                             Archive scraper
#===============================================================================

#===============================================================================
#                             Setup
#===============================================================================

### FULL URL:               https://archive.4plebs.org/pol/thread/263998273/#263998273
fourChanArchive_base_url = 'https://archive.4plebs.org/pol/thread/'

datetime = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#===============================================================================
#                             Get Thread Ids
#===============================================================================

def getThreadIdsFromScrapedThreads():
    fourchanData = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/"
    dataPath = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/2020-06/"
    threadObjectsDict = {}

    ### Get sub directories and files scraped
    subdirs = [x[0] for x in os.walk(fourchanData)]
    subdirs.pop(0) # we must remove the first entry as it is this directory itself

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
                        if 'no' in thread.keys(): 
                            ### If threadId not yet encountered, create new key
                            if thread['no'] not in threadObjectsDict.keys():
                                threadObjectsDict[thread['no']] = thread                          

    return threadObjectsDict.keys()

### Scraped IDs, to be extracted via HTML
listOfThreadIds = getThreadIdsFromScrapedThreads()

# logging
#print (listOfThreadIds)
#print (len(listOfThreadIds))
#print (len(list(set(listOfThreadIds))))

counter = 1

for postId in listOfThreadIds:
    
    ### URL and filename construction
    url = fourChanArchive_base_url + str(postId) + "/#" + str(postId) 
    filename = "fourChanData/" + datetime + '_pol_' + str(postId) + '.html'

    ### Now fetch the URl 
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, "html.parser")

    print ("Saving file [",counter,"] of [",len(listOfThreadIds),"] -> [", filename,"]")
    with open(filename, "w") as file:
        file.write(str(soup))
    
    counter += 1

    ### 8kun will terminate the connection if requests are too frequent (standard DOS protection)
    #time.sleep(1)