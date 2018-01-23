# -*- coding: utf-8 -*-
"""
Created on 07/06/2017

@author: bartosz paszcza
"""
import requests     # used to make rest calls
import json # parse response result
import urllib
import re
import time
import os
import csv

#############################
outputFileName = "3_med"

queries = ["aetiological diagnosis",
            "atherosclerosis diagnosis",
            "atherosclerosis disease",
            "breast cancer mortality rate",
            "cardiac chamber size",
            "chamber quantification",
            "chronic kidney disease diagnosis",
            "chronic kidney disease guideline",
            "chronic kidney disease progression",
            "chronic kidney disease treatment",
            "complication classification",
            "complication management",
            "composite international diagnostic interview",
            "drug craving",
            "drug discovery setting",
            "drug permeability",
            "dsm-iv disorder",
            "echocardiography contrast",
            "fvc maneuver",
            "hcc treatment",
            "heart ischemia",
            "hepatic artery catheterization",
            "hepatobiliary surgeons",
            "high plasma concentrations",
            "hypertension prevention",
            "incentive-sensitization theory",
            "low-density lipoprotein effects",
            "lung cancer risk factor",
            "metabolic syndrome diagnosis",
            "neuritic plaque",
            "neuroadaptation",
            "neurofibrillary change",
            "neuropil thread",
            "obesity measure",
            "plasma cholesterol concentration",
            "pressor agent",
            "thiazide-type diuretic",
            "type 2 diabetes mellitus risk"]
#######################################



######################
#### FUNCTIONS 
########################



def normaliseText(text):
    "function normalisng text to lowercase letters, removing all non-alphanumeric signs"
    text = text.lower()
    text = re.sub('[^a-zA-Z0-9\n\.]', ' ', text)
    text = text.replace(".", "")
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
        if 'Ti' in jsonList[i]:
            jsonList[i]['Ti'] = normaliseText(jsonList[i]['Ti'])
            pluralQuery = str(query+"s") #as Scopus takes into account plural forms of queries (e.g. treatment -> treatments), this was introduced to check whether the exact form of the query is in title (MA, GS - do not take plural forms into account)
            if (query not in jsonList[i]['Ti'] or pluralQuery in jsonList[i]['Ti']):
                listToRemove.append(i)
    invertedList = sorted(listToRemove, reverse=True)
    
    NoRemovedDocs = len(invertedList)
    
    for x in invertedList:
        jsonList.pop(x)
    
    return jsonList, NoRemovedDocs



def iterativelyQueryAPI (MAcademicApi_key, ScopusApi_key, queryPhrase, outputFileName):
    limit = 200
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
    maShortenedResult, maFullResult, maNoDocs, maNoDocsReceived = maPaperSearchByTitle(microsoftApiKey, queryPhrase, maOffset, limit)
    #print("Initial Microsoft Academic query: %d documents retrieved" % maNoDocs)
    maTotalNoDocs = maNoDocs
    scopusShortenedResult, scopusFullResult, scopusNoDocs, scopusNoDocsReceived = scopusSearchByTitle(scopusApiKey, queryPhrase, scopusOffset, limit)
    scopusTotalNoDocs = scopusNoDocs
    #print("Initial Scopus query: %d documents retrieved" % scopusNoDocs)
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
        maShortenedResult, maFullResult, maNoDocs,  maNoDocsReceived = maPaperSearchByTitle(microsoftApiKey, queryPhrase, maOffset,limit)
        maTotalNoDocs = maTotalNoDocs + maNoDocs
        
        #updating lists of results
        maShortened.extend(maShortenedResult)
        maFull.extend(maFullResult['entities'])
        #print("Iterative Microsoft Academic query: %s documents retrieved, offset = %s" % (maNoDocs, maOffset))
    
    while scopusNoDocsReceived >= 200:
        #updating offset
        scopusOffset = scopusOffset + scopusNoDocsReceived
        time.sleep(time_delay)
        
        #reruning query
        scopusShortenedResult, scopusFullResult, scopusNoDocs, scopusNoDocsReceived = scopusSearchByTitle(scopusApiKey, queryPhrase, scopusOffset, limit)
        scopusTotalNoDocs = scopusTotalNoDocs + scopusNoDocs
        
        #updating lists of results
        scopusShortened.extend(scopusShortenedResult)
        scopusFull.extend(scopusFullResult['search-results']['entry'])
        #print("Iterative Scopus query: %s documents retrieved, offset = %s" % (scopusNoDocs, scopusOffset))
        
        #saving full response for future use
    with open('data/original_output/MA_bytitle_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
        json.dump(maFull, outfileInitial)
    
    with open('data/individual_queries/MA_bytitle_%s.json' % outputFileName, 'w+') as outfile:
        json.dump(maShortened, outfile)
        
    #Scopus
    #saving full response for future use
    with open('data/original_output/scopus_bytitle_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
        json.dump(scopusFull, outfileInitial)
        
    #saving shortened json 
    with open('data/individual_queries/scopus_bytitle_%s.json' % outputFileName, 'w+') as outfile:
        json.dump(scopusShortened, outfile)

    
    queryStats = [queryPhrase, maTotalNoDocs, scopusTotalNoDocs]
    print("Retrieved documents for keywords {%s} in title. Number of documents: Microsoft Academic - %s, Scopus - %s" % (queryPhrase, maTotalNoDocs, scopusTotalNoDocs))
    return maFull, maShortened, scopusFull, scopusShortened, queryStats

def maPaperSearchByTitle(api_key, paperTitle, offset, limit):
    #use phrase built from string: And(W='cp', W='invariance') as query
    maSearchQuery = convertStringToMASearchQuery(paperTitle)
                                                                                                          
    #setting up API
    url_search_api = 'https://westus.api.cognitive.microsoft.com/academic/v1.0/evaluate?' # service address 
    headers = {'Ocp-Apim-Subscription-Key':api_key}
    
    paperTitle = normaliseText(paperTitle)
    
    #parameters for query
    parameters = urllib.parse.urlencode({
        'expr': maSearchQuery,
        'count': limit,
        'offset': offset,
        'attributes': 'Ti,Y,CC,ECC,AA.AuN,E',
        'orderby': 'Ti'
        })
    #final REST url
    url = url_search_api + parameters
    
    #processing of respons
    api_response = requests.get(url, headers=headers)
    rawResultJson = json.loads(api_response.content.decode('utf-8'))
    noDocsRetrieved = len(rawResultJson['entities'])
        
    resultJson = rawResultJson
    originalResultJson = rawResultJson
    
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in resultJson['entities']:
        additionalInfo = json.loads(element['E'])
        del element['E']
        #print(additionalInfo)
        
        if 'VFN' in additionalInfo:
            element['Venue'] = {}
            element['Venue']['FullName'] = additionalInfo['VFN']
            if 'I' in additionalInfo: element['Venue']['Issue'] = additionalInfo['I']
            if 'V' in additionalInfo: element['Venue']['Volume'] = additionalInfo['V']
        if 'DOI' in additionalInfo: element['DOI'] = additionalInfo['DOI']
        if 'S' in additionalInfo: element['S'] = additionalInfo['S']
    
    finalJson, noDocsRemoved = FilterForQueryInTitle(paperTitle, resultJson['entities'])
    
    noDocs = noDocsRetrieved - noDocsRemoved
    
    return finalJson, originalResultJson, noDocs,  noDocsRetrieved



def scopusSearchByTitle(api_key, paperTitle, offset, limit):
    url_search_api = 'http://api.elsevier.com/content/search/scopus?' # service address 
    
    paperTitle = normaliseText(paperTitle)
    paperTitleBrackets = '"'+paperTitle+'"'
    
    #print("""title(""" +paperTitleBrackets+ """)""")
    
    parameters = urllib.parse.urlencode({
        'httpAccept': 'application/json',
        'apiKey': scopusApiKey,
        'query': """title(""" +paperTitleBrackets+ """)""",
        'count': limit,
        'start': offset,
        'sort': 'publicationName'
        })
    
    url = url_search_api + parameters
    
    api_response = requests.get(url, headers='')
    rawResultJson = json.loads(api_response.content.decode('utf-8'))
    
    #print(json.dumps(rawResultJson, indent=2, sort_keys=True))
    
    noDocsRetrieved = len(rawResultJson['search-results']['entry'])
    
    outputContent = []
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in rawResultJson['search-results']['entry']:
        #print (element)
        shortenedEntity = {}
        if 'prism:coverDate' in element: shortenedEntity['Y'] = element['prism:coverDate']
        if 'citedby-count' in element: shortenedEntity['CC'] = element['citedby-count']
        if 'dc:identifier' in element: shortenedEntity['Id'] = element['dc:identifier']
        if 'eid' in element: shortenedEntity['eid_scopus'] = element['eid']
        if 'dc:creator' in element: shortenedEntity['AA'] = element['dc:creator']
        if 'dc:title' in element: shortenedEntity['Ti'] = element['dc:title']
        if 'prism:url' in element: shortenedEntity['SU'] = element['prism:url']
        
        if 'prism:publicationName' in element: 
            shortenedEntity['Venue'] = {}
            shortenedEntity['Venue']['FullName'] = element['prism:publicationName']
            if 'prism:issueIdentifier' in element: shortenedEntity['Venue']['Issue'] = element['prism:issueIdentifier']
            if 'prism:volume' in element: shortenedEntity['Venue']['Volume'] = element['prism:volume']
        if 'prism:doi' in element: shortenedEntity['DOI'] = element['prism:doi']
        if 'subtypeDescription' in element: shortenedEntity['Category'] = element['subtypeDescription']
        outputContent.append(shortenedEntity)

    outputContent, noDocsRemoved = FilterForQueryInTitle(paperTitle, outputContent)
    
    noDocs = noDocsRetrieved #- noDocsRemoved
    return outputContent, rawResultJson, noDocs, noDocsRetrieved
        
###################################################################################################
#RUN
#############################################

## Load configuration
con_file = open("config.json")
config = json.load(con_file)
con_file.close()
time_delay = 5

#create lists to append results

maListFull = []
maListShortened = []
scopusListFull = []
scopusListShortened = []
stats = []

## Initialize client
microsoftApiKey = config['microsoft_academic_key'] # Azure Cognitive API Key, replace with your own key
scopusApiKey = config['scopus_key']


#check directories
#verify if folder structre exists, otherwise create
originalOutputFileName = str('data/original_output/MA_keyword_%s_full_response.json' % outputFileName)
disciplinaryFileName = str('data/disciplines/MA_keyword_%s.json' % outputFileName)
indifidualQueriesFileName = str('data/individual_queries/MA_bytitle_%s.json' % outputFileName)
statsFileName = str('logs/stats/MA_and_Scopus_%s.csv' % outputFileName)


os.makedirs(os.path.dirname(originalOutputFileName), exist_ok=True)
os.makedirs(os.path.dirname(disciplinaryFileName), exist_ok=True)
os.makedirs(os.path.dirname(indifidualQueriesFileName), exist_ok=True)
os.makedirs(os.path.dirname(statsFileName), exist_ok=True)





for query in queries:
    queryPhrase = query #Ti
    outputFileNameIndividual = queryPhrase.replace(" ", "_")
    
    (maFull, maShortened, scopusFull, scopusShortened, queryStats) = iterativelyQueryAPI (microsoftApiKey, scopusApiKey, queryPhrase, outputFileNameIndividual)
    
    #append results
    stats.append(queryStats)
    for doc in maFull:
        maListFull.append(doc)
    for doc in maShortened:
        maListShortened.append(doc)
    for doc in scopusFull:
        scopusListFull.append(doc)
    for doc in scopusShortened:
        scopusListShortened.append(doc)
    
    
    #basicStatistics(queryPhrase) #obtain basic statistics and visualise those
    
#save lists of results if querying done 

#save stats
with open(statsFileName,'w+', newline='') as f:
    w = csv.writer(f)
    w.writerows(stats)
    #for entry in stats:
    #    w.writerow(entry)

#microsoft academic
#saving full response for future use
with open(originalOutputFileName, 'w+') as outfileInitial:
    json.dump(maListFull, outfileInitial)

with open(disciplinaryFileName, 'w+') as outfile:
    json.dump(maListShortened, outfile)


#Scopus
#saving full response for future use
with open('data/original_output/scopus_keyword_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
    json.dump(scopusListFull, outfileInitial)
    
#saving shortened json 
with open('data/disciplines/scopus_keyword_%s.json' % outputFileName, 'w+') as outfile:
    json.dump(scopusListShortened, outfile)
