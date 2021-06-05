import json
import os
import bs4
from bs4 import BeautifulSoup, Tag, NavigableString

#===============================================================================
#                           Variables Init
#===============================================================================
eightKunDataDir = "8kun-data/"
firstFile = "2020-06-11_15-00-40_pnd_551.html"
fullFilePath = eightKunDataDir + firstFile

#===============================================================================
#                           Iterative Loop for Multiple Files
#===============================================================================
# ### 1. Iterate through all files in directory
def iterateThroughFilesInDir(directory):
    all8KunThreads = []
    fileCounter = 0
    for fn in os.listdir(directory):
        fullFilePath = os.path.join(directory, fn)
        num_files = len([f for f in os.listdir(directory)if os.path.isfile(os.path.join(directory, f))])
        print ("parsing file [", fileCounter, "] of [", num_files, "] in ", fullFilePath)

        ### extract the id of the thread from the filename and use to search html
        leftSideFN, iDAndHTML = fn  .split("pnd_",1)
        threadId, HTML = iDAndHTML.split(".",1)
        #print(threadId)
        ### parse the file, and return a thread object
        soup = BeautifulSoup(open(fullFilePath), features="lxml")        
        threadObject = openAndParseDataFromHTMLFile(soup, threadId)
        all8KunThreads.append(threadObject)
        
        fileCounter += 1
        
    return all8KunThreads

#===============================================================================
#                           Attribute Extraction
#===============================================================================

### TODO: Find a cleaner solution 
# -> This is hacky, we cannot be sure that the first "post_anchor" indeed contains the ID
# -> IF ID contains "op" or "thread" - verfify this: <div class="post op has-file body-not-empty" id="op_2942">
def getThreadId(soup):
    if soup.find(class_="post_anchor") is not None:
        return soup.find(class_="post_anchor")['id']
    else:
        return ''

def getThreadTitle(soup):
    if soup.find(class_="subject") is not None:
        return soup.find(class_="subject").text
    else:
        return ''

def  getThreadText(soup, threadId):
    text = ''
    if soup.find(id="op_"+threadId) is not None:
        for child in soup.find(id="op_"+threadId).descendants:
            if type(child) is bs4.element.Tag:
                if 'class' in child.attrs:
                    if child['class'][0] == "body-line":
                        #print(child.text)
                        text = text + child.text
    return text


def getThreadTextAll(soup, threadId):
    text = ''
    if soup.find(id="op_"+threadId) is not None:
        for child in soup.find(id="op_"+threadId).descendants:
            if type(child) is bs4.element.NavigableString:
                text = text + child
    return text

def getComments(soup, threadId):
    comments = []
    if soup.find(id="thread_"+threadId) is not None:
        for child in soup.find(id="thread_"+threadId).descendants:
            comment = {}
            if type(child) is bs4.element.Tag:
                if 'id' in child.attrs:
                    if "reply_" in child['id']:
                        text, commentId = child['id'].split('_',1) # text var is not needed so ignore it
                        #print(">> COMMENT_ID:", commentId)
                        comment['comment_Id'] = commentId
                        comment_body = ""
                        for grandchild in child.descendants:
                            if type(grandchild) is bs4.element.Tag:
                                if 'class' in grandchild.attrs:
                                    if grandchild['class'][0] == "body-line":
                                        comment_body = comment_body + grandchild.text + " "
                                        comment['comment_Body'] = comment_body
                                elif 'time' in grandchild.name: # get post time
                                        if 'datetime' in grandchild.attrs: 
                                            comment['creationDate'] = grandchild['datetime']
                        #print(comment)
                        comments.append(comment)

        #print(len(comments))
        #print(comments)

    return comments


def getThreadCreationDate(soup, threadId):
    creationDate = ''
    if soup.find(id="op_"+threadId) is not None:
        for child in soup.find(id="op_"+threadId).descendants:
            if type(child) is bs4.element.Tag:
                if 'datetime' in child.attrs:
                    creationDate = child['datetime']
    return creationDate

#===============================================================================
#                           Object Building
#===============================================================================

## 2. Open HMTL file with Soup
def openAndParseDataFromHTMLFile(soup, threadId):
    eightKunThread = {
        'thread_Id' : getThreadId(soup),
        'thread_title' : getThreadTitle(soup),
        'thread_text_body' : getThreadText(soup, threadId),
        'thread_text_all' : getThreadTextAll(soup, threadId),
        'thread_creation_date' : getThreadCreationDate(soup, threadId),
        'comments' : getComments(soup, threadId)
    }
    return eightKunThread

#===============================================================================
#                                   Main
#===============================================================================

### The directory iterator returns a huge JSON with all threads and their comments. the file contains duplicates
all8KunThreads = iterateThroughFilesInDir(eightKunDataDir)
with open("8kun-scraped-threads-all.json", 'w') as f:
    json.dump(all8KunThreads, f)

#prettyPrintFile(fullFilePath, "8kun_pretty_post2.html")

#===============================================================================
#                           Helper Functions
#===============================================================================

def prettyPrintFile(inputFilePath, outputFileName):
    soup = BeautifulSoup(open(inputFilePath), features="lxml")

    with open(outputFileName, "w") as file:
        file.write(str(soup.prettify()))