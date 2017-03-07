# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 17:00:00 2017

@author: bartosz
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:22:10 2017

@author: bartosz paszcza
"""
import requests     # used to make rest calls
import json # parse response result
import urllib
import re
import time
from basicSearchAnalysis import basicStatistics

def normaliseText(text):
    "function normalisng text to lowercase letters, removing all non-alphanumeric signs"
    text = text.lower()
    text = re.sub('[^a-zA-Z0-9\n\.]', ' ', text)
    text = " ".join(text.split())
    return (text)

def convertStringToMASearchQuery (text):
    words = text.split()
    #use phrase built from string: And(W='cp', W='invariance')
    if len(words) == 1:
        result = str("""W='%s'""" % words[0])
    else:
        result = str("""And(W='%s'""" % words[0])
        for word in words[1:]:
            phrase = str(""", W='%s'""" % word)
            result = str(result+phrase)
        result = result + ')'
    return result

def FilterForQueryInTitle (stringSearchedFor, jsonList):
    query = normaliseText(stringSearchedFor)
    listToRemove = []
    for i in range(len(jsonList)):
        if query not in jsonList[i]['Ti']:
            listToRemove.append(i)
    invertedList = sorted(listToRemove, reverse=True)
    for x in invertedList:
        jsonList.pop(x)
    
    return jsonList



def iterativelyQueryAPI (MAcademicApi_key, ScopusApi_key, queryPhrase, filename):
    queryPhrase = normaliseText(queryPhrase)
    maOffset = 0
    scopusOffset = 0
    maTotalNoDocs = 0
    scopusTotalNoDocs = 0
    
    maShortened = []
    maFull = []
    scopusShortened = []
    scopusFull = []
    
    #make initial query, output -> no of docs retrieved, 
    print("Initial query performed...")
    maShortenedResult, maFullResult, maNoDocsReceived = maPaperSearchByTitle(microsoftApiKey, queryPhrase, outputFileName, maOffset)
    print("Initial Microsoft Academic query: %d documents retrieved" % maNoDocsReceived)
    scopusShortenedResult, scopusFullResult, scopusNoDocsReceived = scopusSearchByTitle(scopusApiKey, queryPhrase, outputFileName, scopusOffset)
    print("Initial Scopus query: %d documents retrieved" % scopusNoDocsReceived)
    #append obtained docs to a stored lists of resutls
    maShortened.extend(maShortenedResult)
    maFull.extend(maFullResult['entities'])
    scopusShortened.extend(scopusShortenedResult)
    scopusFull.extend(scopusFullResult['search-results']['entry'])
    
    while maNoDocsReceived >= 200:
        #updating offset
        maOffset = maOffset + maNoDocsReceived
        time.sleep(time_delay)
        
        #reruninng query
        maShortenedResult, maFullResult, maNoDocsReceived = maPaperSearchByTitle(microsoftApiKey, queryPhrase, outputFileName, maOffset)
        
        #updating lists of results
        maShortened.extend(maShortenedResult)
        maFull.extend(maFullResult['entities'])
        print("Iterative Microsoft Academic query: %s documents retrieved, offset = %s" % (maNoDocsReceived, maOffset))
    
    while scopusNoDocsReceived >= 200:
        #updating offset
        scopusOffset = scopusOffset + scopusNoDocsReceived
        time.sleep(time_delay)
        
        #reruning query
        scopusShortenedResult, scopusFullResult, scopusNoDocsReceived = scopusSearchByTitle(scopusApiKey, queryPhrase, outputFileName, scopusOffset)
        
        #updating lists of results
        scopusShortened.extend(scopusShortenedResult)
        scopusFull.extend(scopusFullResult['search-results']['entry'])
        print("Iterative Scopus query: %s documents retrieved, offset = %s" % (scopusNoDocsReceived, scopusOffset))
        
    maTotalNoDocs = maOffset + maNoDocsReceived
    scopusTotalNoDocs = scopusOffset + scopusNoDocsReceived
    
    #save lists of results if querying done 
    
    #microsoft academic
    #saving full response for future use
    with open('data/fullversions/MA_bytitle_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
        json.dump(maFull, outfileInitial)
    
    with open('data/MA_bytitle_%s.json' % outputFileName, 'w+') as outfile:
        json.dump(maShortened, outfile)
        
    #Scopus
    #saving full response for future use
    with open('data/fullversions/scopus_bytitle_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
        json.dump(scopusFull, outfileInitial)
        
    #saving shortened json 
    with open('data/scopus_bytitle_%s.json' % outputFileName, 'w+') as outfile:
        json.dump(scopusShortened, outfile)
        
    print("Retrieved documents for keywords {%s} in title, saved to JSON files. Number of documents: Microsoft Academic - %s, Scopus - %s" % (queryPhrase, maTotalNoDocs, scopusTotalNoDocs))

def maPaperSearchByTitle(api_key, paperTitle, outputFileName, offset):
    #use phrase built from string: And(W='cp', W='invariance') as query
    maSearchQuery = convertStringToMASearchQuery(paperTitle)
                                                                                                          
    #setting up API
    url_search_api = 'https://westus.api.cognitive.microsoft.com/academic/v1.0/evaluate?' # service address 
    headers = {'Ocp-Apim-Subscription-Key':api_key}
    
    paperTitle = normaliseText(paperTitle)
    
    #parameters for query
    parameters = urllib.parse.urlencode({
        'expr': maSearchQuery,
        'count': '200',
        'offset': offset,
        'attributes': 'Ti,Y,CC,ECC,AA.AuN,AA.AuId,E',
        'orderby': 'Ti'
        })
    #final REST url
    url = url_search_api + parameters
    
    #processing of respons
    api_response = requests.get(url, headers=headers)
    rawResultJson = json.loads(api_response.content.decode('utf-8'))
    noDocsRetrieved = len(rawResultJson['entities'])
        
    resultJson = rawResultJson
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in resultJson['entities']:
        additionalInfo = json.loads(element['E'])
        del element['E']
        #print(additionalInfo)
        element['Venue'] = {}
        if 'VFN' in additionalInfo:
            element['Venue']['FullName'] = additionalInfo['VFN']
            if 'I' in additionalInfo: element['Venue']['Issue'] = additionalInfo['I']
            if 'V' in additionalInfo: element['Venue']['Volume'] = additionalInfo['V']
        if 'DOI' in additionalInfo: element['DOI'] = additionalInfo['DOI']
    
    finalJson = FilterForQueryInTitle(paperTitle, resultJson['entities'])
    
    return finalJson, rawResultJson, noDocsRetrieved



def scopusSearchByTitle(api_key, paperTitle, outputFileName, offset):
    url_search_api = 'http://api.elsevier.com/content/search/scopus?' # service address 
    
    parameters = urllib.parse.urlencode({
        'httpAccept': 'application/json',
        'apiKey': scopusApiKey,
        'query': """title('"""+paperTitle+"""')""",
        'count': '200',
        'start': offset,
        'sort': 'publicationName'
        })
    
    url = url_search_api + parameters
    
    api_response = requests.get(url, headers='')
    rawResultJson = json.loads(api_response.content.decode('utf-8'))
    
    #print(json.dumps(res_json, indent=2, sort_keys=True))
    
    noDocsRetrieved = len(rawResultJson['search-results']['entry'])
    
    
    outputContent = []
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in rawResultJson['search-results']['entry']:
        #print (element)
        shortenedEntity = {}
        if 'prism:coverDate' in element: shortenedEntity['Y'] = element['prism:coverDate']
        if 'citedby-count' in element: shortenedEntity['CC'] = element['citedby-count']
        if 'dc:identifier' in element: shortenedEntity['Id'] = element['dc:identifier']
        if 'dc:creator' in element: shortenedEntity['AA'] = element['dc:creator']
        if 'dc:title' in element: shortenedEntity['Ti'] = element['dc:title']
        shortenedEntity['Venue'] = {}
        if 'prism:publicationName' in element: 
            shortenedEntity['Venue']['FullName'] = element['prism:publicationName']
            if 'prism:issueIdentifier' in element: shortenedEntity['Venue']['Issue'] = element['prism:issueIdentifier']
            if 'prism:volume' in element: shortenedEntity['Venue']['Volume'] = element['prism:volume']
        if 'prism:doi' in element: shortenedEntity['DOI'] = element['prism:doi']
        if 'subtypeDescription' in element: shortenedEntity['Category'] = element['subtypeDescription']
        outputContent.append(shortenedEntity)
        
    return outputContent, rawResultJson, noDocsRetrieved
        
###################################################################################################
#RUN


## Load configuration
con_file = open("config.json")
config = json.load(con_file)
con_file.close()
time_delay = 5

## Initialize client
microsoftApiKey = config['microsoft_academic_key'] # Azure Cognitive API Key, replace with your own key
scopusApiKey = config['scopus_key']
queryPhrase = 'supersonic molecular beam' #Ti
outputFileName = queryPhrase.replace(" ", "_")

iterativelyQueryAPI (microsoftApiKey, scopusApiKey, queryPhrase, outputFileName)

basicStatistics(queryPhrase) #obtain basic statistics and visualise those
