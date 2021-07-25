#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 11:27:49 2017

@author: paszczak
"""
import json
import itertools
import re
import unicodedata
import pprint
pp = pprint.PrettyPrinter(indent=4)

def SimplifyAuthorsInGoogleScholar (nameList):
    #Google scholar format: BM Paszcza; Scopus format: Paszcza B.; MA format: mess - bartosz paszcza, paszcza bartosz, b m paszcza
    newList = []
    
    for name in nameList:
        name = name.replace(".", "")
        name = name.split(None, 1)
        try:
            name = name[1]
            name = re.sub('[^a-zA-Z0-9\n\.]', ' ', name)
            name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
            
            
        except IndexError:
            name = ""  # no surname
        #name = name.split(None, 1)[1]
        name = name.lower()
        newList.append(str(name))
        
    return newList

def SimplifyAuthorsInScopus (nameList):
    #Google scholar format: BM Paszcza; Scopus format: Paszcza B.; MA format: mess - bartosz paszcza, paszcza bartosz, b m paszcza
    newList = []
    for name in nameList:
        name = name.replace(".", "")
        name = name.replace("-","")
        name = name.rsplit(None, 1)[0]
        name = name.lower()
        
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
        
            
        newList.append(str(name))
    return newList
    
def SimplifyAuthorsInMA (nameList):
    newList = []
    for name in nameList:
        name = name.lower()
        name = name.replace(".", "")
        names = name.split()
        for element in names:
            element = re.sub('[^a-zA-Z0-9\n\.]', ' ', element)
            element = unicodedata.normalize('NFKD', element).encode('ASCII', 'ignore')
            
            newList.append(str(element))
    
    return newList
    #Google scholar format: BM Paszcza; Scopus format: Paszcza B.; MA format: mess - bartosz paszcza, paszcza bartosz, b m paszcza
    #remove initials: start from beggining, if single letter followed by space (on place 0) -> remove those two signs, repeat
    

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


def unifySchema(doc):
    if "_ - S - _ - U" in doc:
        doc["_ - SU"] = str(doc["_ - S - _ - U"]).split(", ")
        doc.pop("_ - S - _ - U", None)
    elif "_ - SU" in doc:
        doc["_ - SU"] = str(doc["_ - SU"]).split(", ")
    elif "_ - S" in doc:
        doc["_ - SU"] = str(doc["_ - S"]).split(", ")
    
    if "_ - AA - _ - AuN" in doc:
        doc["_ - AA"] = str(doc["_ - AA - _ - AuN"]).split(", ")
        doc.pop("_ - AA - _ - AuN", None)
    elif "_ - AA" in doc:
        doc["_ - AA"] = str(doc["_ - AA"]).split(", ")
    elif "_ - AA - _ - name" in doc:
        doc["_ - AA"] = str(doc["_ - AA - _ - name"]).split(", ")
        doc.pop("_ - AA - _ - name", None)
        
    doc["simplifiedTi"] = simplifyTitle(doc["_ - Ti"])
    
    return doc


###########################################
###
#           OPEN FILES
###
##########################################

directory= "data/overlapGoldenSample/"

#read in matches, read in conflicts
with open(str(directory+"overlap_400_matches2.json")) as data_file:    
    matchesJson = json.load(data_file)
with open(str(directory+"overlap_400_matches2_CONFLICTS.json")) as conflict_file:
    conflictJson = json.load(conflict_file)
    
limit = 400
filename = "_keyword_1_natural_sciences.json"
directory= "data/filteredJSONs/"

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
        
        #with open(str(directory+"MA_sample"+filename), 'w') as fp:
        #    json.dump(maJson400, fp)
        
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
        
        #with open(str(directory+"scopus_sample"+filename), 'w') as fp:
        #    json.dump(scopusJson400, fp)

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


###########################################
###
#           CODE
###
##########################################

def findRecord (searchedID, dictionary):
    for element in dictionary:
        if element["_ - Id"] == searchedID:
            record = element
    return record

def showRecords (matchedRecord):
    fullRecord = []
    if 'maID' in matchedRecord:
        doc = findRecord (matchedRecord['maID'], maJson)
        fullRecord.append(doc)
    if 'scopusID' in matchedRecord:
        doc = findRecord (matchedRecord['scopusID'], scopusJson)
        fullRecord.append(doc)
    if 'gsID' in matchedRecord:
        doc = findRecord (matchedRecord['gsID'], gsJson)
        fullRecord.append(doc)
    
    return fullRecord

def prettyPrinter (doc, match):
    pp.pprint(doc)
    pp.pprint(match)
    print("matchedRecord:")
    pp.pprint(showRecords(doc))
    print("matchedRecordConflict:")
    pp.pprint(showRecords(match))
    input("Press Enter to continue...")

#foreach in conflicts, get id, search if id present in matches
for match in conflictJson:
    conflictFound = 0
    if 'maID' in match:
        print(match['maID'])
        for doc in matchesJson:
            if 'maID' in doc:
                if doc['maID'] == match['maID']:
                    print("maID matched: %s" % match['maID'])
                    prettyPrinter (doc, match)
                    
                    conflictFound = conflictFound+1
        
    if 'scopusID' in match:
        print(match['scopusID'])
        for doc in matchesJson:
            if 'scopusID' in doc:
                if doc['scopusID'] == match['scopusID']:
                    print("scopusID matched: %s"%match['scopusID'])
                    prettyPrinter (doc, match)
                    conflictFound = conflictFound+1
        
    if 'gsID' in match:
        print(match['gsID'])
        for doc in matchesJson:
            if 'gsID' in doc:
                if doc['gsID'] == match['gsID']:
                    print("gsID matched: %s"%match['gsID'])
                    prettyPrinter (doc, match)
                    conflictFound = conflictFound+1
                    
    print("**************************")
    
#if not present - get the other id, repeat

#if id found in matched and conflicts -> print those ids that do not match, or whole matches
