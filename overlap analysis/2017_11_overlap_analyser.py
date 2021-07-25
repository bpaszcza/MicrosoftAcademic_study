#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 15:12:11 2017

@author: paszczak
"""


import json
import re
import itertools
#from pprint import pprint
#import sys
import unicodedata
import difflib
import csv
# load sample of 400!!!

#metaConditionsThreshold = 1  - defined dynamically below




matchedRecords = []
### data cleansing - improved

#Ti -> simplified Titles, removing spaces, repeated letters, vowels
#Ti -> simplified Titles, removing spaces, repeated letters, vowels
def simplifyTitle (text):
    """function normalisng text to lowercase letters, removing all non-alphanumeric signs, then removing all spaces, repeated (double) letters, and vowels from string"""
    text = text.lower()
    # remove ' inf ', ' sub ' - in MA such notation is used to denote subscripts etc.;
    text = text.replace(' inf ','')
    text = text.replace(' sup ','')
    
    #limiting title string to 150 chars, the maximum in Google Scholar
    text = text[:148]
    
    text = re.sub('[^a-zA-Z0-9\n\.]', ' ', text)
    
    
    text = text.replace(".", "")
    text = text.replace(" ", "")
    text = " ".join(text.split())
    
    text = ''.join(ch for ch, _ in itertools.groupby(text)) #remove all repeated letters, illiterate -> iliterate
    
    vowels = ('a', 'e', 'i', 'o', 'u')
    text = ''.join([l for l in text if l not in vowels]) #remove all vowels
    
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
    
    text = str(text).encode('utf-8')
    return (str(text))


def matchRecords (doc1, doc2, condition, titleSimilarityThreshold):
    #pubyear2 = int(doc2["_ - Y"])
    #pubyearRange = range((pubyear2-1),(pubyear2+2),1)
    jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
    jointURL = [i for i in doc1["_ - SU"] if i in doc2["_ - SU"]]
    if "_ - DOI" in doc1 and "_ - DOI" in doc2:
        if doc1["_ - DOI"] is not None and doc2["_ - DOI"] is not None:
            jointDOI = [i for i in doc1["_ - DOI"] if i in doc2["_ - DOI"]]
        else:
            jointDOI = []
    else:
        jointDOI = []
    
    titleOverlap = difflib.SequenceMatcher(None, doc1["simplifiedTi"], doc2["simplifiedTi"]).ratio()
    
    titleMatch = 0
    yearMatch = 0
    authorMatch = 0
    doiurlMatch = 0
    venueMatch= 0
    askedForConfirmation = 0
    
    
    if titleOverlap >= titleSimilarityThreshold:
        titleMatch = 1        
    if doc1["_ - Y"] == doc2["_ - Y"]:
        yearMatch = 1    
    if len(jointAuthor) != 0:
        authorMatch = 1
    if len(jointURL) + len(jointDOI) > 0:
        doiurlMatch = 1
    if doc1["simplifiedVenue"] == doc2["simplifiedVenue"]:
        venueMatch = 1
        #askForConfirmation ("fully matched, confirm merge?", default="yes")
    
    sumofflags = titleMatch + yearMatch + authorMatch + doiurlMatch + venueMatch
        
    if (sumofflags >= condition):
        mergeConfirmation = True
        #print ("Title, Pub Year, Authors - matched; records hence matched")
        #print (mergeConfirmation)
    else:
        mergeConfirmation = 0
        
    #else:
        #question = str("title match: %s, publ year match: %s, author match: %s" % (titleMatch, yearMatch, authorMatch))
        #mergeConfirmation = askForConfirmation (question, doc1, doc2, default="yes")
        #askedForConfirmation = 1
    
    
    return (mergeConfirmation, doc1, doc2, askedForConfirmation)



# DOI/URL
def matchDOI(jsonList1, jsonList2, doicount, metaConditionsThreshold):
    matchedEntry = {}
    questionCount = 0
    
    for doc1 in jsonList1:
        if doc1["_ - DOI"] is not None:
            for doc2 in jsonList2:
                if doc2["_ - DOI"] == doc1["_ - DOI"]:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) =  matchRecords(doc1, doc2, metaConditionsThreshold, 0.95)
                    questionCount = questionCount + askedConfirmation
                    if mergeConfirmation == True:
                        #print("yup! maid %s, scopusID %s" % (doc1["_ - Id"],doc2["_ - Id"]))
                        
                        matchedEntry["scopusID"] = c["_ - Id"] #scopusID
                        matchedEntry["maID"] = b["_ - Id"] #ma ID
                        
                        flag = 0
                        for element in matchedRecords:
                            if element["maID"] == b["_ - Id"]:
                                flag = 1
                                #print(matchedRecords)
                                #print("ids found already: elementid %s, newid %s" % (element["maID"], b["_ - Id"]))
                        if flag == 0:
                            matchedRecords.append(dict(matchedEntry))
                            #print("appended new matched record")
                        
                        #print(doc1, "/n" ,doc2)
                        doicount = doicount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
                        
    #input("Match by DOI ended, with %s entries matched and %s questions asked, press enter..." % (doicount, questionCount))
    return doicount, questionCount
                    
def matchURLs (jsonList1, jsonList2, urlcount, metaConditionsThreshold):
    matchedEntry = {}
    questionCount = 0
    for doc2 in jsonList2:
        if doc2["_ - SU"] is not None:
            for doc1 in jsonList1:
                jointURL = [i for i in doc1["_ - SU"] if i in doc2["_ - SU"]]
                if len(jointURL) > 0:
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 0.95)
                    questionCount = questionCount +askedConfirmation
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        flag = 0
                        for element in matchedRecords:
                            if element["maID"] == b["_ - Id"]:
                                element["gsID"] = c["_ - Id"]
                                flag = 1
                                #print("extended matched record!")
                        if flag == 0:
                                matchedEntry = {}
                                matchedEntry["maID"] = b["_ - Id"]
                                matchedEntry["gsID"] = c["_ - Id"]
                                matchedRecords.append(dict(matchedEntry))
                                #print("appended new matched record")
                        
                        urlcount = urlcount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
    #input("Match by URL ended, with %s entries matched and %s questions asked, press enter..." % (urlcount, questionCount))
                    
    return urlcount, questionCount


def matchTitleSimilar(jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #matchedEntry = {}
    questionCount = 0
    tiSimilarityThreshold = 0.95
    
    for doc1 in jsonList1:
        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                titleOverlap = difflib.SequenceMatcher(None, doc1["simplifiedTi"], doc2["simplifiedTi"]).ratio()
                
                #jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                if titleOverlap > tiSimilarityThreshold:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, tiSimilarityThreshold)
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        submissionArray = appendMatchTitle (b, c, idString1, idString2, submissionArray)
                        titlecount = titlecount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
                        
    return titlecount, questionCount, submissionArray




def appendMatchTitle(doc1, doc2, idString1, idString2, submissionArray):
    
    flag = 1
    recordPos = 0
    
    matchedEntry = {}
    matchedEntry[idString1] = doc1["_ - Id"]
    matchedEntry[idString2] = doc2["_ - Id"]
    
    for element in submissionArray:
        
        shared_keyvals = set(element.items()) & set(matchedEntry.items())
        """
        logic:
            if 2 keyval pairs the same- do not append duplicate
            if in the loop no match or conflicting match found (meaning: 0-2 shared keys AND 0 shared keyvals or 2 shared keys AND 1 shared keyvals)
            if 1 shared keyvals & 1 shared key -> update record with new, non-conflicting key-val pair
            """
        
        if len(shared_keyvals) == 2:
            #exact same match found, change flag in order not to add new entry
            flag = 0
        elif len(shared_keyvals) == 1:
            recordPos = submissionArray.index(element)
            
            if idString2 not in element:
                flag = 0
                element[idString2] = doc2["_ - Id"]
                submissionArray[recordPos].update(element)
            elif idString1 not in element:
                element[idString1] = doc1["_ - Id"]
                submissionArray[recordPos].update(element)
                flag = 0
                
                
    if flag == 1:
        submissionArray.append(dict(matchedEntry))
        #print("appended new matched record")
        
    
    return submissionArray

def countOverlap (matchedRecords):
    counterGSMAScopus = 0
    counterGSMA = 0
    counterGSScopus = 0
    counterMAScopus = 0
    
    
    
    for match in matchedRecords:
        gsID = 0
        maID = 0
        scopusID = 0
        
        if "gsID" in match:
            gsID = 1
        if "maID" in match:
            maID = 1
        if "scopusID" in match:
            scopusID = 1
        
        if gsID == 1 and maID == 1 and scopusID == 1:
            counterGSMAScopus = counterGSMAScopus+1
        if gsID == 1 and maID == 1 and scopusID == 0:
            counterGSMA = counterGSMA + 1
        if gsID == 1 and maID == 0 and scopusID == 1:
            counterGSScopus = counterGSScopus +1
        if gsID == 0 and maID == 1 and scopusID == 1:
            counterMAScopus = counterMAScopus + 1

################
"""load jsons + convert schema to needed format (authors, sources urls -> lists of strings, 
simplifyTitle, unify authors to surnames in GS and Scopus; correct NoneType to string/ints)

"""

limit = 400

with open(str(directory+"MA"+filename)) as data_file:    
    maJson = json.load(data_file)
    maJson400 = []
    x = 0
    for doc in maJson:
        doc = unifySchema(doc)
        doc["_ - AA"] = SimplifyAuthorsInMA(doc["_ - AA"])
        doc["_ - Venue - FullName"] = str(doc["_ - Venue - FullName"] or "")
        doc["_ - Venue - Issue"] = str(doc["_ - Venue - Issue"] or "")
        doc["_ - Venue - Volume"] = str(doc["_ - Venue - Volume"] or "")
        
        if x < limit:
            maJson400.append(doc)
            x = x+1
        
    with open(str(directory+"MA_sample400"+filename), 'w+') as fp:
            json.dump(maJson400, fp)
        
with open(str(directory+"scopus"+filename)) as data_file:    
    scopusJson = json.load(data_file)
    scopusJson400 = []
    x = 0
    
    for doc in scopusJson:
        doc = unifySchema(doc)
        doc["_ - AA"] = SimplifyAuthorsInScopus(doc["_ - AA"])
        doc["_ - Venue - Issue"] = str(doc["_ - Venue - Issue"] or "")
        doc["_ - Venue - Volume"] = str(doc["_ - Venue - Volume"] or "")
        doc["_ - Y"] = int(doc["_ - Y"][:4])
        doc["_ - CC"] = int(doc["_ - CC"])
        
        if x < limit:
            scopusJson400.append(doc)
            x = x+1
        
    with open(str(directory+"scopus_sample400"+filename), 'w+') as fp:
            json.dump(scopusJson400, fp)

with open(str(directory+"google_scholar"+filename)) as data_file:    
    gsJson = json.load(data_file)
    gsJson400 = []
    x = 0
    for doc in gsJson:
        doc = unifySchema(doc)
        doc["_ - Id"] = x
        doc["_ - AA"] = SimplifyAuthorsInGoogleScholar(doc["_ - AA"])
        doc["_ - Y"] = int(doc["_ - Y"] or "0") 
        doc["_ - CC"] = int(doc["_ - CC"] or "0")
        doc["_ - gsType"] = str(doc["_ - gsType"] or "none")
        
        if x < limit:
            gsJson400.append(doc)
        x = x+1
    
    
    #with open(str(directory+"google_scholar"+filename), 'w+') as fp:
    #    json.dump(gsJson, fp)
    
    with open(str(directory+"google_scholar_sample400"+filename), 'w+') as fp:
        json.dump(gsJson400, fp)
    
### calculate overlaps


# cleansed ca400 records from each database
filename = "_keyword_1_natural_sciences.json"
directory= "data/filteredJSONs/"

with open(str(directory+"google_scholar_sample400"+filename), 'r') as fp:
    gsJson400 = json.load(fp)

with open(str(directory+"MA_sample400"+filename), 'r') as fp:
    maJson400 = json.load(fp)

with open(str(directory+"scopus_sample400"+filename), 'r') as fp:
    scopusJson400 = json.load(fp)
    
doicount = 0
urlcount = 0


maScopCount = 0
gsScopCount = 0
gsMaCount = 0
metaConditionsThreshold = 2


print("doi-url matching...")
#DOI matching: SCOPUS <-> MA, both sides
(doicount, questionCountDOI)  = matchDOI (maJson400, scopusJson400, doicount, metaConditionsThreshold)
#askForConfirmation ("finished matching DOIs, begin with URLs (GoogleScholar - MA)?", "", "", default="yes")
(urlcount, questionCountURL) = matchURLs (maJson400, gsJson400, urlcount, metaConditionsThreshold)

print("title matching...")
(maScopCount, questionCountTitle, matchedRecords) = matchTitleSimilar (maJson400, scopusJson400, "maID", "scopusID", maScopCount, matchedRecords, metaConditionsThreshold)
(gsScopCount, questionCountTitle, matchedRecords) = matchTitleSimilar (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, matchedRecords, metaConditionsThreshold)
(gsMaCount, questionCountTitle, matchedRecords) = matchTitleSimilar (gsJson400, maJson400, "gsID", "maID", gsMaCount, matchedRecords, metaConditionsThreshold)
