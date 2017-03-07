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

def normaliseText(text):
    "function normalisng text to lowercase letters, removing all non-alphanumeric signs"
    text = text.lower()
    text = re.sub('[^a-zA-Z0-9\n\.]', ' ', text)
    text = " ".join(text.split())
    return (text)



def maPaperSearchByTitle(api_key, paperTitle, outputFileName):
    #setting up API
    url_search_api = 'https://westus.api.cognitive.microsoft.com/academic/v1.0/evaluate?' # service address 
    headers = {'Ocp-Apim-Subscription-Key':api_key}
    
    paperTitle = normaliseText(paperTitle)
    
    #parameters for query
    parameters = urllib.parse.urlencode({
        'expr': """Ti=='%s'""" % (paperTitle),
        'count': '205',
        'attributes': 'Ti,Y,CC,ECC,AA.AuN,AA.AuId,E'
        })
    #final REST url
    url = url_search_api + parameters
    
    #processing of respons
    api_response = requests.get(url, headers=headers)
    resultJson = json.loads(api_response.content.decode('utf-8'))
    
    #saving full response for future use
    with open('data/MA_bytitle_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
        json.dump(resultJson, outfileInitial)
    
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in resultJson['entities']:
        additionalInfo = json.loads(element['E'])
        del element['E']
        #print(additionalInfo)
        element['Venue'] = {}
        element['Venue']['FullName'] = additionalInfo['VFN']
        element['Venue']['Issue'] = additionalInfo['I']
        element['Venue']['Volume'] = additionalInfo['V']
        element['DOI'] = additionalInfo['DOI']
    
    #saving shortened json 
    with open('data/MA_bytitle_%sjson' % outputFileName, 'w+') as outfile:
        json.dump(resultJson['entities'], outfile)



def scopusSearchByTitle(api_key, paperTitle, outputFileName):
    url_search_api = 'http://api.elsevier.com/content/search/scopus?' # service address 
    
    parameters = urllib.parse.urlencode({
        'httpAccept': 'application/json',
        'apiKey': scopusApiKey,
        'query': """title('"""+paperTitle+"""')""",
        'count': '200'
        })
    
    url = url_search_api + parameters
    
    api_response = requests.get(url, headers='')
    resultJson = json.loads(api_response.content.decode('utf-8'))
    
    #print(json.dumps(res_json, indent=2, sort_keys=True))
    
    #saving full response for future use
    with open('data/scopus_bytitle_%s_full_response.json' % outputFileName, 'w+') as outfileInitial:
        json.dump(resultJson, outfileInitial)
    
    outputContent = []
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in resultJson['search-results']['entry']:
        #print (element)
        shortenedEntity = {}
        shortenedEntity['Y'] = element['dc:identifier']
        shortenedEntity['CC'] = element['citedby-count']
        shortenedEntity['Id'] = element['dc:identifier']
        shortenedEntity['AA'] = element['dc:creator']
        shortenedEntity['Ti'] = element['dc:title']
        shortenedEntity['Venue'] = {}
        shortenedEntity['Venue']['FullName'] = element['prism:publicationName']
        shortenedEntity['Venue']['Issue'] = element['prism:issueIdentifier']
        shortenedEntity['Venue']['Volume'] = element['prism:volume']
        shortenedEntity['DOI'] = element['prism:doi']
        shortenedEntity['Category'] = element['subtypeDescription']
        outputContent.append(shortenedEntity)
    
    
    #saving shortened json 
    with open('data/scopus_bytitle_%s.json' % outputFileName, 'w+') as outfile:
        json.dump(outputContent, outfile)
        
###################################################################################################

## Load configuration
con_file = open("config.json")
config = json.load(con_file)
con_file.close()

## Initialize client
microsoftApiKey = config['microsoft_academic_key'] # Azure Cognitive API Key, replace with your own key
scopusApiKey = config['scopus_key']
paperTitle = 'quantum' #Ti
outputFileName = paperTitle

paperTitle = normaliseText(paperTitle)

maPaperSearchByTitle(microsoftApiKey, paperTitle, outputFileName)
scopusSearchByTitle(scopusApiKey, paperTitle, outputFileName)