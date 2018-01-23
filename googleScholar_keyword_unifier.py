# -*- coding: utf-8 -*-
"""
Created on Mon May  8 12:22:40 2017

@author: bartosz
"""

from pathlib import Path
import json
import re
import csv
import os

#########################################
#######   functions
#########################################


def normaliseText(text):
    "function normalisng text to lowercase letters, removing all non-alphanumeric signs"
    text = text.lower()
    text = re.sub('[^a-zA-Z0-9\n\.]', ' ', text)
    text = text.replace(".", "")
    text = " ".join(text.split())
    return (text)

def FilterForQueryInTitle (stringSearchedFor, jsonList):
    query = normaliseText(stringSearchedFor)
    listToRemove = []
    for i in range(len(jsonList)):
        titleNormalised = normaliseText(jsonList[i]['Ti'])
        if query not in titleNormalised:
            listToRemove.append(i)
    invertedList = sorted(listToRemove, reverse=True)
    for x in invertedList:
        jsonList.pop(x)
    
    return jsonList

#google scholar function to unify schema!!!! omitting [CITATION] in Google Scholar -> 

def googleScholarSchemaUnifier (json_data):
    outputContent = []
    outputIndexedContent = []
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in json_data:
        #print (element)
        #create new element which is to have unified schema
        
        shortenedEntity = {}
        if 'authors' in element: shortenedEntity['AA'] = element['authors']
        if 'cites' in element: shortenedEntity['CC'] = element['cites']
        if 'title' in element: shortenedEntity['Ti'] = normaliseText(element['title'])
        if 'source' in element: shortenedEntity['Venue'] = element['source']
        if 'year' in element: shortenedEntity['Y'] = element['year']
        if 'type' in element: shortenedEntity['gsType'] = element ['type']
        if 'article_url' in element: shortenedEntity['S'] = element ['article_url']
        
        #if already transformed to a new format, copy
        if 'AA' in element: shortenedEntity = element
        if 'SU' in element: 
            shortenedEntity['S'] = element ['SU']
            del shortenedEntity['SU']
        if 'Ti' in element: shortenedEntity['Ti'] = normaliseText(element['Ti'])
        
        outputIndexedContent.append(shortenedEntity) #if select only docs without [citation] marking in gs, change to outputContent
        
        #count of GS docs without '[CITATION]' type documents (without verified source / link)
        """if 'gsType' not in shortenedEntity: 
            outputIndexedContent.append(shortenedEntity)
        elif shortenedEntity['gsType'] != 'CITATION':
            outputIndexedContent.append(shortenedEntity)"""
        
    return(outputContent, outputIndexedContent)

def parsingJsonFile (fullFileName):
    with open(fullFileName, encoding="utf8") as gs_data_file:    
        json_data = json.load(gs_data_file)
    
    #print(json_data)
    # filter for query in title of each document (iterate through list)
    (gsListUnifiedWithCITATION, gsListUnifiedWithoutCITATION)  = googleScholarSchemaUnifier (json_data)
    #print(gsListUnifiedWithoutCITATION[0])
    
    gsListFiltered = FilterForQueryInTitle (query, gsListUnifiedWithoutCITATION)
    
    # create stats: how many documents with phrase in title found for each query
    noDocs = len(gsListFiltered)
    noCitations = 0
    for doc in gsListFiltered:
        if 'CC' in doc: docCitations = int(doc['CC'])
        else: docCitations=0
        noCitations = noCitations + docCitations
    
    
    
    # save to a joint file (append to large array), print stats (?)
    for doc in gsListFiltered:
        gsListShortened.append(doc)
        
    with open(fullFileName, 'w+') as outfile:
        json.dump(gsListFiltered, outfile)
    queryStats = [query, noDocs]
    print ("query: %s, docs: %s, citations: %s" % (query, noDocs, noCitations))
    
    return queryStats

########################################
#code
##########################################


noDocsStats = []
noCitationStats = []
gsListShortened = []
noKeywordFilesFound = 0
stats = []


outputFileName = "1_natural_sciences"
queries = ["dna sequence similarity",
           "protein sequence similarity",
            "psi blast",
            "single crystal diffraction data",
            "gene regulatory molecule",
            "sensor network design",
            "sensor network architecture",
            "Gold Nanoparticles assembly",
            "Gold Nanoparticles application",
            "Scalable molecular dynamics",
            "namd",
            "molecular dynamics force field",
            "biocore",
            "carrier spin polarization",
            "spin electronics",
            "photoelectric emission spectra",
            "chemiluminescent electron transfer",
            "hydrocarbon film",
            "ZnO material",
            "ZnO device",
            "ZnO semiconductor",
            "mitochondrial electron-transport chain",
            "ubiquitin system",
            "covalent ligation",
            "Ubiquitin-mediated degradation",
            "ubiquitin-mediated process",
            "Complex networks structure",
            "Complex networks dynamics",
            "graphene oxide chemistry",
            "graphene oxide synthesis",
            "G1-phase progression",
            "INK4 proteins",
            "oligosaccharide units",
            "oligosaccharide sequence",
            "quark-mixing matrix",
            "big bang cosmology",
            "accelerator physics",
            "meson properties",
            "erbb signalling network",
            "signaling pathway network"]
            

for query in queries:
    # from list of queries, read query, find file with that query in title
    
    query2 = normaliseText(query)
    queryFileName = query2.replace(" ", "_")
    fullFileName = Path("data/individual_queries/gs_1_"+queryFileName+".json")
    
    if fullFileName.exists():
        #print ("<%s> data found" % query)
        noKeywordFilesFound = noKeywordFilesFound + 1
        fullFileName = str("data/individual_queries/gs_1_"+queryFileName+".json")
        queryStats = parsingJsonFile(fullFileName)
        stats.append(queryStats)
    else:
        print ("<%s> data NOT FOUND, filename: %s" % (query, fullFileName))
    
# save
#saving shortened json 

if noKeywordFilesFound == len(queries):
    print ("All queries data files found: OK!")


statsFileName = str('logs/stats/gs_%s.csv' % outputFileName)
dataFileName = str('data/disciplines/google_scholar_keyword_%s.json' % outputFileName)


#verify if folder structre exists, otherwise create
os.makedirs(os.path.dirname(statsFileName), exist_ok=True)
os.makedirs(os.path.dirname(dataFileName), exist_ok=True)

#print (stats)
#save stats and filtered data
with open(statsFileName,'w+', newline='') as f:
    w = csv.writer(f)
    w.writerows(stats)
    #for entry in stats:
    #    w.writerow(entry)

with open(dataFileName, 'w+') as outfile:
    json.dump(gsListShortened, outfile)
    
    
