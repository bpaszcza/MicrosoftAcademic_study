# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 13:59:27 2017

@author: bartosz
"""

#########################################
#######   functions
#########################################




#google scholar function to unify schema!!!! 

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
