#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 17:03:39 2017

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





authorMatchedRecords = []
yearMatchedRecords = []
title95MatchedRecords = []
venueMatchedRecords = []
doiUrlmatchedRecords = []
title80MatchedRecords = []
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
                    (mergeConfirmation, b, c, askedConfirmation) =  matchRecords(doc1, doc2, metaConditionsThreshold, 1)
                    questionCount = questionCount + askedConfirmation
                    if mergeConfirmation == True:
                        #print("yup! maid %s, scopusID %s" % (doc1["_ - Id"],doc2["_ - Id"]))
                        
                        matchedEntry["scopusID"] = c["_ - Id"] #scopusID
                        matchedEntry["maID"] = b["_ - Id"] #ma ID
                        
                        flag = 0
                        for element in doiUrlmatchedRecords:
                            if element["maID"] == b["_ - Id"]:
                                flag = 1
                                #print(matchedRecords)
                                #print("ids found already: elementid %s, newid %s" % (element["maID"], b["_ - Id"]))
                        if flag == 0:
                            doiUrlmatchedRecords.append(dict(matchedEntry))
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
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 1)
                    questionCount = questionCount +askedConfirmation
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        flag = 0
                        for element in doiUrlmatchedRecords:
                            if element["maID"] == b["_ - Id"]:
                                element["gsID"] = c["_ - Id"]
                                flag = 1
                                #print("extended matched record!")
                        if flag == 0:
                                matchedEntry = {}
                                matchedEntry["maID"] = b["_ - Id"]
                                matchedEntry["gsID"] = c["_ - Id"]
                                doiUrlmatchedRecords.append(dict(matchedEntry))
                                #print("appended new matched record")
                        
                        urlcount = urlcount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
    #input("Match by URL ended, with %s entries matched and %s questions asked, press enter..." % (urlcount, questionCount))
                    
    return urlcount, questionCount

titleMatchedRecords = []    
metadataMatchedRecords = []   

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


# Ti
# remove ' inf ' or ' sub '

def matchTitle(jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #matchedEntry = {}
    questionCount = 0
    
    for doc1 in jsonList1:
        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                #jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                if doc2["simplifiedTi"] == doc1["simplifiedTi"]:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 1.0)
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        submissionArray = appendMatchTitle (b, c, idString1, idString2, submissionArray)
                        titlecount = titlecount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
                        
    return titlecount, questionCount, submissionArray

def matchCombined(jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #matchedEntry = {}
    questionCount = 0
    
    for doc1 in jsonList1:
        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                titleOverlap = difflib.SequenceMatcher(None, doc1["simplifiedTi"], doc2["simplifiedTi"]).ratio()
                #jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                if titleOverlap > 0.95:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 0.95)
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        submissionArray = appendMatchTitle (b, c, idString1, idString2, submissionArray)
                        titlecount = titlecount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
                        
    return titlecount, questionCount, submissionArray

def matchTitleSimilar(tiSimilarityThreshold, jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #matchedEntry = {}
    questionCount = 0
    
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


def matchVenue(jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #matchedEntry = {}
    questionCount = 0
    
    for doc1 in jsonList1:
        if doc1["simplifiedVenue"] is not "b\"b'nn'\"" or doc1["simplifiedVenue"] is not "b\"b''\"":
            for doc2 in jsonList2:
                #titleOverlap = difflib.SequenceMatcher(None, doc1["simplifiedTi"], doc2["simplifiedTi"]).ratio()
                
                #jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                if doc2["simplifiedVenue"] == doc1["simplifiedVenue"]:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 1.0)
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        submissionArray = appendMatchTitle (b, c, idString1, idString2, submissionArray)
                        titlecount = titlecount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
                        
    return titlecount, questionCount, submissionArray

def matchAuthor (jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #questionCount = 0
    
    for doc1 in jsonList1:
        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                if len(jointAuthor) != 0:
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 1.0)
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        submissionArray = appendMatchTitle (b, c, idString1, idString2, submissionArray)
                        
                        titlecount = titlecount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
    
    questionCount = 0
    return titlecount, questionCount, submissionArray

def matchYear (jsonList1, jsonList2,idString1, idString2, titlecount, submissionArray, metaConditionsThreshold):
    #questionCount = 0
    
    for doc1 in jsonList1:
        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                #jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                if doc1["_ - Y"] ==doc2["_ - Y"]:
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, metaConditionsThreshold, 1.0)
                    if mergeConfirmation == True:
                        #print("yup!")
                        
                        submissionArray = appendMatchTitle (b, c, idString1, idString2, submissionArray)
                        
                        titlecount = titlecount+1
                    #elif mergeConfirmation == False:
                        #print("merge declined manually")
    
    questionCount = 0
    return titlecount, questionCount, submissionArray


### compare with golden standard

def calculateOverlap (x,y):
    overlapFlag = 0
    
    for element in x:
        if "maID" in element:
            for match in y:
                if "maID" in match:
                    if element["maID"] == match["maID"]:
                        shared_items = set(element.items()) & set(match.items())
                        if len(element) == len(shared_items) and len(element) == len(match):
                            overlapFlag = overlapFlag+1
        elif "gsID" in element:
            for match in y:
                if "gsID" in match:
                    if element["gsID"] == match["gsID"]:
                        shared_items = set(element.items()) & set(match.items())
                        if len(element) == len(shared_items) and len(element) == len(match):
                            overlapFlag = overlapFlag+1
    precision = overlapFlag/(len(x))
    recall = overlapFlag/(len(y))
    F = 2 * (precision * recall)/(precision+recall)
    
    resultsArray = []
    resultsArray.append(precision)
    resultsArray.append(recall)
    resultsArray.append(F)
    
    return resultsArray
    
    


############ reading in files
# golden standard sample of matches
directory= "data/overlapGoldenSample/"
with open(str(directory+"overlap_400_matches2.json")) as data_file:
    #data = list(data_file)
    matchesJson = json.load(data_file)



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
metaConditionsThreshold = 0

for i in range(1,6):
    metaConditionsThreshold = i
    print(metaConditionsThreshold)
    print("metaConditionThreshold")
    
    print("doi-url matching...")
    #DOI matching: SCOPUS <-> MA, both sides
    (doicount, questionCountDOI)  = matchDOI (maJson400, scopusJson400, doicount, metaConditionsThreshold)
    #askForConfirmation ("finished matching DOIs, begin with URLs (GoogleScholar - MA)?", "", "", default="yes")
    (urlcount, questionCountURL) = matchURLs (maJson400, gsJson400, urlcount, metaConditionsThreshold)
    
    print("title matching...")
    (maScopCount, questionCountTitle, titleMatchedRecords) = matchTitle (maJson400, scopusJson400, "maID", "scopusID", maScopCount, titleMatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, titleMatchedRecords) = matchTitle (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, titleMatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, titleMatchedRecords) = matchTitle (gsJson400, maJson400, "gsID", "maID", gsMaCount, titleMatchedRecords, metaConditionsThreshold)
    
    print("author matching...")
    (maScopCount, questionCountTitle, authorMatchedRecords) = matchAuthor (maJson400, scopusJson400, "maID", "scopusID", maScopCount, authorMatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, authorMatchedRecords) = matchAuthor (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, authorMatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, authorMatchedRecords) = matchAuthor (gsJson400, maJson400, "gsID", "maID", gsMaCount, authorMatchedRecords, metaConditionsThreshold)
    
    print("pubyear matching...")
    (maScopCount, questionCountTitle, yearMatchedRecords) = matchYear (maJson400, scopusJson400, "maID", "scopusID", maScopCount, yearMatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, yearMatchedRecords) = matchYear (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, yearMatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, yearMatchedRecords) = matchYear (gsJson400, maJson400, "gsID", "maID", gsMaCount, yearMatchedRecords, metaConditionsThreshold)
    
    print("title_similar 1 matching...")
    (maScopCount, questionCountTitle, title80MatchedRecords) = matchTitleSimilar (0.9, maJson400, scopusJson400, "maID", "scopusID", maScopCount, title80MatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, title80MatchedRecords) =  matchTitleSimilar (0.9, gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, title80MatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, title80MatchedRecords) =  matchTitleSimilar (0.9, gsJson400, maJson400, "gsID", "maID", gsMaCount, title80MatchedRecords, metaConditionsThreshold)
    
    print("title_similar 2 matching...")
    (maScopCount, questionCountTitle, title95MatchedRecords) =  matchTitleSimilar (0.95, maJson400, scopusJson400, "maID", "scopusID", maScopCount, title95MatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, title95MatchedRecords) = matchTitleSimilar (0.95, gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, title95MatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, title95MatchedRecords) = matchTitleSimilar (0.95, gsJson400, maJson400, "gsID", "maID", gsMaCount, title95MatchedRecords, metaConditionsThreshold)
    
    print("pub venue matching...")
    (maScopCount, questionCountTitle, venueMatchedRecords) = matchVenue (maJson400, scopusJson400, "maID", "scopusID", maScopCount, venueMatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, venueMatchedRecords) = matchVenue (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, venueMatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, venueMatchedRecords) = matchVenue (gsJson400, maJson400, "gsID", "maID", gsMaCount, venueMatchedRecords, metaConditionsThreshold)
    
    
    
    #doiURLresults = calculateOverlap (doiUrlmatchedRecords, matchesJson)
    combinedMatchedRecords = list(doiUrlmatchedRecords)
    
    print("combined matching...")
    (maScopCount, questionCountTitle, combinedMatchedRecords) = matchCombined (maJson400, scopusJson400, "maID", "scopusID", maScopCount, combinedMatchedRecords, metaConditionsThreshold)
    (gsScopCount, questionCountTitle, combinedMatchedRecords) = matchCombined (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount, combinedMatchedRecords, metaConditionsThreshold)
    (gsMaCount, questionCountTitle, combinedMatchedRecords) = matchCombined (gsJson400, maJson400, "gsID", "maID", gsMaCount, combinedMatchedRecords, metaConditionsThreshold)
    
    
    
    doiURLresults = calculateOverlap (doiUrlmatchedRecords, matchesJson)
    titleResults = calculateOverlap (titleMatchedRecords, matchesJson)
    title80Results = calculateOverlap (title80MatchedRecords, matchesJson)
    title95results = calculateOverlap (title95MatchedRecords, matchesJson)
    venueResults = calculateOverlap (venueMatchedRecords, matchesJson)
    authorResults = calculateOverlap (authorMatchedRecords, matchesJson)
    yearResults = calculateOverlap (yearMatchedRecords, matchesJson)
    combinedResults = calculateOverlap (combinedMatchedRecords, matchesJson)
    
    
    header = ["precision", "recall", "F"]
    rows = zip(header, doiURLresults, titleResults, title80Results, title95results, venueResults, authorResults, yearResults, combinedResults)
    directory= "data/overlapGoldenSample/"
    with open(str(directory+"testResults.csv"), 'a') as myfile:
        wr = csv.writer(myfile, delimiter=";")
        
        
        for val in rows:
            wr.writerow(val)
        
        print("resetting tables")
        doiUrlmatchedRecords = []
        titleMatchedRecords = []
        title80MatchedRecords = []
        authorMatchedRecords = []
        yearMatchedRecords = []
        title95MatchedRecords = []
        venueMatchedRecords = []
        combinedMatchedRecords = []
        
        
        #(metadataprecision, metadatarecall, metadataURLf) = calculateOverlap (doiUrlmatchedRecords, matchesJson)
