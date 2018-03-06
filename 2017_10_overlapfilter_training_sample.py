# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
import re
import itertools
from pprint import pprint
import sys
import unicodedata
import difflib

""" FINDING NAMES:
    name = "nakano"
    for doc in maJson:
        for names in doc["_ - AA"]"
            if name in names:
                print(doc)


"""

doicount = 0
urlcount = 0
mergequestions = 0
titlecount = 0

recordsMatched = []

#AA (authors) -> surnames (coherent format)

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

"""
def matchDOIs(record1, table2):
    if record1['DOI'] is in table2:
        #show what has been matched for review

def matchURLs(record1, table2):
    for url in record1['_ - S - _ - U']:
        if url is in table2:
            #show which record to be matched (title, year, authors)
"""
def addComment (question):
    sys.stdout.write(question)
    comment = input()
    return comment

def askForConfirmation (question, doc1, doc2, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        pprint(doc1)
        print(" ")
        pprint(doc2)
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
"""
def matchRecords(record1, record2):
    if record1['simplifiedTi'] == record2['simplifiedTi']:
        pubyear = record1['Y']
        pubrange = range((pubyear-1), (pubyear+2), 1)
        if record1['Y'] in pubrange:
            author = record1['simplifiedAA']
            if author in record2['simplifiedAA']:
                #show what has been matched, match

            else:
                #show what has been proposed to match, wait for the reply
        else: #show what has been proposed to match, wait for reply

    return
"""
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

    if "_ - Venue" in doc:
        doc["simplifiedVenue"] = simplifyTitle(str(doc["_ - Venue"]))
        #doc.pop("_ - AA - _ - AuN", None)
    elif "_ - Venue - FullName" in doc:
        doc["simplifiedVenue"] = simplifyTitle(str(doc["_ - Venue - FullName"]))


    doc["simplifiedTi"] = simplifyTitle(doc["_ - Ti"])

    return doc

def matchRecords (doc1, doc2, condition):
    pubyear2 = int(doc2["_ - Y"])
    pubyearRange = range((pubyear2-1),(pubyear2+2),1)
    jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]

    titleMatch = 0
    yearMatch = 0
    authorMatch = 0
    askedForConfirmation = 0


    if doc1["simplifiedTi"] == doc2["simplifiedTi"]:
        titleMatch = 1
    if doc1["_ - Y"] == doc2["_ - Y"]:
        yearMatch = 1
    if len(jointAuthor) != 0:
        authorMatch = 1
        #askForConfirmation ("fully matched, confirm merge?", default="yes")

    sumofflags = titleMatch + yearMatch + authorMatch

    if (sumofflags >= condition):
        mergeConfirmation = True
        print ("Title, Pub Year, Authors - matched; records hence matched")
        print (mergeConfirmation)

    else:
        question = str("title match: %s, publ year match: %s, author match: %s" % (titleMatch, yearMatch, authorMatch))
        mergeConfirmation = askForConfirmation (question, doc1, doc2, default="yes")
        askedForConfirmation = 1


    return (mergeConfirmation, doc1, doc2, askedForConfirmation)



""" String similarity - use Levensthein:


import difflib
difflib.SequenceMatcher(None, 'hello world', 'hello').ratio()
"""
matchedRecords = []
matchedRecordsConflict = []

def appendMatchTitle(doc1, doc2, idString1, idString2):

    flag = 0
    additionalFlag = 0
    recordPos = 0

    matchedEntry = {}
    matchedEntry[idString1] = doc1["_ - Id"]
    matchedEntry[idString2] = doc2["_ - Id"]

    for element in matchedRecords:
        if idString1 in element:
            if element[idString1] == doc1["_ - Id"]:
                recordPos = matchedRecords.index(element)
                flag = flag+1
                additionalFlag = 1
                if idString2 in element:
                    flag = flag+1
                    if element[idString2] == doc2["_ - Id"]:
                        flag = flag+1

    for element in matchedRecords:
        if idString2 in element:
            if element[idString2] == doc2["_ - Id"]:
                recordPos = matchedRecords.index(element)
                flag = flag+1
                additionalFlag = 2
                if idString1 in element:
                    flag = flag+1
                    if element[idString1] == doc1["_ - Id"]:
                        flag = flag+1
    #FLAG VALUES
    #0 = neither of IDs in matchedRecords, appending new match;
    if flag == 0:
        matchedRecords.append(dict(matchedEntry))
        print("appended new matched record")
    #1- one of IDs in mRecord, but without other - adding new key value pair to existing match
    elif flag == 1:
        print("match with ID already found, adding new id to the record...")
        if additionalFlag == 1:
            element = {}
            element[idString2] = doc2["_ - Id"]
            matchedRecords[recordPos].update(element)
            print(matchedRecords[recordPos])

        elif additionalFlag == 2:
            element = {}
            element[idString1] = doc1["_ - Id"]
            matchedRecords[recordPos].update(element)
            print(matchedRecords[recordPos])
    #2 - one of IDs in mRecord, other one exists, but does not match - CONFLICT, appending new match  to conflictRecords
    elif flag == 2:
        matchedEntry["conflictNotInKey"] = additionalFlag
        matchedRecordsConflict.append(dict(matchedEntry))
        print("conflicT, appending to matchedRecordsConflict!")
    #3 - match already in mRecord (both IDs match)
    elif flag == 6:
        print("exact same match already found, proceeding further...")
    #if >3 - raise error!
    elif (flag > 6 or 2< flag <6):
        print("ERROR: something went wrong... flag value >6 or between 2 and 6")
        #print("id's: firstone %s, secondone %s" % (doc1["_ - Id"], doc2["_ - Id"]))


def matchTitle(jsonList1, jsonList2, idString1, idString2, titlecount):
    #matchedEntry = {}
    questionCount = 0


    for doc1 in jsonList1:

        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                jointAuthor = [i for i in doc1["_ - AA"] if i in doc2["_ - AA"]]
                #find overlap over simplified titles
                titleOverlap = difflib.SequenceMatcher(None, doc1["simplifiedTi"], doc2["simplifiedTi"]).ratio()
                pubyear2 = int(doc2["_ - Y"])
                pubyearRange = range((pubyear2-1),(pubyear2+2),1)
                flagExists = 0

                for match in matchedRecords:
                    if idString1 in match and idString2 in match:
                        if doc1["_ - Id"] == match[idString1] and doc2["_ - Id"] == match[idString2]:
                            flagExists = 1

                if flagExists == 1:
                    print("match already recorded")
                elif (titleOverlap > 0.8) or (len(jointAuthor) != 0 and int(doc1["_ - Y"]) in pubyearRange):
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2, 3)
                    if mergeConfirmation == True:
                        print("yup!")

                        appendMatchTitle (b, c, idString1, idString2)
                        titlecount = titlecount+1
                    elif mergeConfirmation == False:
                        print("merge declined manually")

    input("Match by Title ended, with %s entries matched and %s questions asked, press enter..." % (titlecount, questionCount))
    return titlecount, questionCount



def matchDOI(jsonList1, jsonList2, doicount):
    matchedEntry = {}
    questionCount = 0

    for doc1 in jsonList1:
        if doc1["_ - DOI"] is not None:
            for doc2 in jsonList2:
                if doc2["_ - DOI"] == doc1["_ - DOI"]:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2,1)
                    questionCount = questionCount + askedConfirmation
                    if mergeConfirmation == True:
                        print("yup! maid %s, scopusID %s" % (doc1["_ - Id"],doc2["_ - Id"]))

                        matchedEntry["scopusID"] = c["_ - Id"] #scopusID
                        matchedEntry["maID"] = b["_ - Id"] #ma ID

                        flag = 0
                        for element in matchedRecords:
                            if element["maID"] == b["_ - Id"]:
                                flag = 1
                                print(matchedRecords)
                                print("ids found already: elementid %s, newid %s" % (element["maID"], b["_ - Id"]))
                        if flag == 0:
                            matchedRecords.append(dict(matchedEntry))
                            print("appended new matched record")

                        #print(doc1, "/n" ,doc2)
                        doicount = doicount+1
                    elif mergeConfirmation == False:
                        print("merge declined manually")
    input("Match by DOI ended, with %s entries matched and %s questions asked, press enter..." % (doicount, questionCount))

    return doicount, questionCount

def matchURLs (jsonList1, jsonList2, urlcount):
    matchedEntry = {}
    questionCount = 0
    for doc2 in jsonList2:
        if doc2["_ - SU"] is not None:
            for doc1 in jsonList1:
                if doc2["_ - SU"] in doc1["_ - SU"]:
                    (mergeConfirmation, b, c, askedConfirmation) = matchRecords(doc1, doc2,1)
                    questionCount = questionCount +askedConfirmation
                    if mergeConfirmation == True:
                        print("yup!")

                        flag = 0
                        for element in matchedRecords:
                            if element["maID"] == b["_ - Id"]:
                                element["gsID"] = c["_ - Id"]
                                flag = 1
                                print("extended matched record!")
                        if flag == 0:
                                matchedEntry = {}
                                matchedEntry["maID"] = b["_ - Id"]
                                matchedEntry["gsID"] = c["_ - Id"]
                                matchedRecords.append(dict(matchedEntry))
                                print("appended new matched record")

                        urlcount = urlcount+1
                    elif mergeConfirmation == False:
                        print("merge declined manually")
    input("Match by URL ended, with %s entries matched and %s questions asked, press enter..." % (urlcount, questionCount))

    return urlcount, questionCount

# reading in jsons, reading column names, etc.
filename = "_keyword_1_natural_sciences.json"
directory= "data/filteredJSONs/"


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


#matchedDocs = []

#DOI matching: SCOPUS <-> MA, both sides
(doicount, questionCountDOI)  = matchDOI (maJson400, scopusJson400, doicount)
#askForConfirmation ("finished matching DOIs, begin with URLs (GoogleScholar - MA)?", "", "", default="yes")
(urlcount, questionCountURL) = matchURLs (maJson400, gsJson400, urlcount)

maScopCount = 0
gsScopCount = 0
gsMaCount = 0
"""(maScopCount, questionCountTitle) = matchTitle (maJson400, scopusJson400, "maID", "scopusID", maScopCount)
(gsScopCount, questionCountTitle) = matchTitle (gsJson400, scopusJson400, "gsID", "scopusID", gsScopCount)
(gsMaCount, questionCountTitle) = matchTitle (gsJson400, maJson400, "gsID", "maID", gsMaCount)
"""
#(titlecount, questionCountTitle) = matchTitle (gsJson400, scopusJson400, gsScopCount)
#(titlecount, questionCountTitle) = matchTitle (gsJson400, maJson400, gsMaCount)

with open('overlap_400_matches2.json', 'w') as fp:
    json.dump(matchedRecords, fp)

with open('overlap_400_matches2_CONFLICTS.json','w') as fp:
    json.dump(matchedRecordsConflict, fp)
   


#(titlecount, questionCountTi) = matchTitle (maJson, gsJson, titlecount)

#match DOIs -> scopus & MA; see if years similar and titles the same -> merge; otherwise - ask
