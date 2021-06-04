import json
import os
import bs4
from bs4 import BeautifulSoup, Tag, NavigableString

#===============================================================================
#                           Variables Init
#===============================================================================

### Actual source
fourChanDataDir = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/fourChanDataArchive/"

### Test source
fourChanTestDataDir = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/testDataFourChan/"

### Test soruce 2
fourChanTestDataDir2 = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/box/"

### Test File
prettyFileDir = "/Users/andrew/Research/Data/Covid-11Jun-to-04Aug-2020/4chan-data/test4chanPretty/"

threadIds = []

#===============================================================================
#                           Attribute Extraction
#===============================================================================

### TODO: Find a cleaner solution 
# -> This is hacky, we cannot be sure that the first "post_anchor" indeed contains the ID
# -> IF ID contains "op" or "thread" - verfify this: <div class="post op has-file body-not-empty" id="op_2942">
def getThreadId(soup):
    # threadId = 0
    # for metaTag in soup.find_all('meta'):
    #     if "content" in metaTag.attrs:
    #         if "Thread #" in metaTag["content"]:
    #             threadId = metaTag["content"].split("#",1)[1]

   return soup.find('article')['id']

def getThreadTitle(soup):
    return soup.find(class_="post_title").text

def  getThreadText(soup, threadId):
    return soup.find("div", class_="text").text


### Remove for 4 chan 
def getThreadTextAll(soup, threadId):
    text = ''
    if soup.find(id="op_"+threadId) is not None:
        for child in soup.find(id="op_"+threadId).descendants:
            if type(child) is bs4.element.NavigableString:
                text = text + child
    return text

def getComments(soup, threadId):
    comments = []
    index = 1
    for articleTag in soup.find_all('article'):
        comment = {}
        if index < 2: 
            index+=1
            pass # first "article" is actually the header of the post, not a comment, so skip
        else:
            # there seem to be article tags that do not refer to comments,
            # so only if they have an id do we treat them as comments
            if 'id' in articleTag.attrs: 
                comment['comment_Id'] = articleTag['id']
                for child in articleTag.descendants:
                    if type(child) is bs4.element.Tag:
                        if 'div' in child.name:
                            if 'class' in child.attrs:
                                if 'text' in child['class']:
                                    comment['comment_Body'] = child.text
                                    #print(child.text)
                                    #print("=============")
                        elif 'time' in child.name: # get post time
                            if 'datetime' in child.attrs: 
                                comment['creationDate'] = child['datetime']
                        elif 'span' in child.name: # get unique commenter Id (comment is stil anon but probably id is tied to IP uniqueness)
                            if 'class' in child.attrs: 
                                if 'poster_hash' in child['class']:
                                    comment['user_Id'] = child.text[3:]
                comments.append(comment)
            index+=1

    return comments

def getThreadCreationDate(soup, threadId):
    return soup.find("time")['datetime']

#===============================================================================
#                           Object Building
#===============================================================================

## 2. Open HMTL file with Soup
def openAndParseDataFromHTMLFile(soup, threadId):
    comments = getComments(soup, threadId)
    fourChanThread = {
        'thread_Id' : getThreadId(soup),
        'thread_title' : getThreadTitle(soup),
        'thread_text_body' : getThreadText(soup, threadId),
        'thread_creation_date' : getThreadCreationDate(soup, threadId),
        'number_comments' : len(comments),
        'comments' : comments
    }
    return fourChanThread

#===============================================================================
#                           Iterative Loop for Multiple Files
#===============================================================================
# ### 1. Iterate through all files in directory
def iterateThroughFilesInDir(directory):
    all4ChanThreads = []
    fileCounter = 0
    for fn in os.listdir(directory):
        fullFilePath = os.path.join(directory, fn)
        num_files = len([f for f in os.listdir(directory)if os.path.isfile(os.path.join(directory, f))])

        # encountered a bug where a MacOS .DS-Store broke the script. Only parse .html files
        if ".html" in fullFilePath:
            ### parse the file, and return a thread object
            soup = BeautifulSoup(open(fullFilePath), features="lxml")

            if soup.find('article') is None:
                print ("WARN: SKIPPING file (Error 404) [", fileCounter, "] of [", num_files, "] in ", fullFilePath)
            else:
                print ("parsing file [", fileCounter, "] of [", num_files, "] in ", fullFilePath)
                threadId = getThreadId(soup)
                threadObject = openAndParseDataFromHTMLFile(soup, threadId)
                all4ChanThreads.append(threadObject)
        else:
            print ("WARN: SKIPPING file (not HTML) [", fileCounter, "] of [", num_files, "] in ", fullFilePath)
        
        fileCounter += 1
        
    return all4ChanThreads

#===============================================================================
#                                   Main
#===============================================================================

### The directory iterator returns a huge JSON with all threads and their comments. the file contains duplicates
all4ChanThreads = iterateThroughFilesInDir(fourChanDataDir)
with open("data/4chan-scraped-threads-all.json", 'w') as f:
    json.dump(all4ChanThreads, f)

### TESt Directory / Sample
# all4ChanThreads = iterateThroughFilesInDir(fourChanTestDataDir)
# with open("data/4chan-scraped-threads-sample.json", 'w') as f:
#     json.dump(all4ChanThreads, f)

#firstFile = "2020-09-22_23-36-51_pol_124205675.html"
#fullFilePath = fourChanDataDir + firstFile

#prettyFile = "4chan_pretty_post.html"
#prettyFilePath = prettyFileDir + prettyFilePath
#prettyPrintFile(fullFilePath, "data/4chan_pretty_post.html")

#===============================================================================
#                           Helper Functions
#===============================================================================

def prettyPrintFile(inputFilePath, outputFileName):
    soup = BeautifulSoup(open(inputFilePath), features="lxml")

    with open(outputFileName, "w") as file:
        file.write(str(soup.prettify()))

