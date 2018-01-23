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
        newList.append(name)

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


        newList.append(name)
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

            newList.append(element)

    return newList
    #Google scholar format: BM Paszcza; Scopus format: Paszcza B.; MA format: mess - bartosz paszcza, paszcza bartosz, b m paszcza
    #remove initials: start from beggining, if single letter followed by space (on place 0) -> remove those two signs, repeat


#Ti -> simplified Titles, removing spaces, repeated letters, vowels
def simplifyTitle (text):
    """function normalisng text to lowercase letters, removing all non-alphanumeric signs, then removing all spaces, repeated (double) letters, and vowels from string"""
    text = text.lower()
    text = re.sub('[^a-zA-Z0-9\n\.]', ' ', text)
    text = text.replace(".", "")
    text = text.replace(" ", "")
    text = " ".join(text.split())

    text = ''.join(ch for ch, _ in itertools.groupby(text)) #remove all repeated letters, illiterate -> iliterate

    vowels = ('a', 'e', 'i', 'o', 'u')
    text = ''.join([l for l in text if l not in vowels]) #remove all vowels

    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')

    text = str(text).encode('utf-8')
    return (text)

"""
def matchDOIs(record1, table2):
    if record1['DOI'] is in table2:
        #show what has been matched for review

def matchURLs(record1, table2):
    for url in record1['_ - S - _ - U']:
        if url is in table2:
            #show which record to be matched (title, year, authors)
"""

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
        doc["_ - SU"] = str(doc["_ - S"])

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
    if doc1["_ - Y"] in pubyearRange:
        yearMatch = 1
    if len(jointAuthor) != 0:
        authorMatch = 1
        #askForConfirmation ("fully matched, confirm merge?", default="yes")

    sumofflags = titleMatch + yearMatch + authorMatch

    if (sumofflags >= condition):
        mergeConfirmation = True
        print ("Title, Pub Year, Authors - matched; records hence matched")

    else:
        question = str("title match: %s, publ year match: %s, author match: %s" % (titleMatch, yearMatch, authorMatch))
        mergeConfirmation = askForConfirmation (question, doc1, doc2, default="yes")
        askedForConfirmation = 1


    return (mergeConfirmation, doc1, doc2, askedForConfirmation)



""" String similarity - use Levensthein:


import difflib
difflib.SequenceMatcher(None, 'hello world', 'hello').ratio()
"""


def matchTitle(jsonList1, jsonList2, titlecount):
    matchedEntries = []
    questionCount = 0

    for doc1 in jsonList1:
        if doc1["simplifiedTi"] is not None:
            for doc2 in jsonList2:
                if doc2["simplifiedTi"] == doc1["simplifiedTi"]:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (a, b, c, askedConfirmation) = matchRecords(doc1, doc2, 3)
                    questionCount = questionCount + askedConfirmation
                    print("yup!")
                    #print(doc1, "/n" ,doc2)
                    titlecount = titlecount+1
    return titlecount, questionCount

def matchDOI(jsonList1, jsonList2, doicount):
    matchedEntries = []
    questionCount = 0

    for doc1 in jsonList1:
        if doc1["_ - DOI"] is not None:
            for doc2 in jsonList2:
                if doc2["_ - DOI"] == doc1["_ - DOI"]:
                    #print (doc1["simplifiedTi"],doc2["simplifiedTi"])
                    (a, b, c, askedConfirmation) = matchRecords(doc1, doc2,3)
                    questionCount = questionCount +askedConfirmation
                    print("yup!")
                    #print(doc1, "/n" ,doc2)
                    doicount = doicount+1
    return doicount, questionCount

def matchURLs (jsonList1, jsonList2, urlcount):
    matchedEntries = []
    questionCount = 0
    for doc2 in jsonList2:
        if doc2["_ - SU"] is not None:
            for doc1 in jsonList1:
                if doc2["_ - SU"] in doc1["_ - SU"]:
                    (a, b, c, askedConfirmation) = matchRecords(doc1, doc2,3)
                    questionCount = questionCount +askedConfirmation
                    print("yup!")
                    urlcount = urlcount+1

    return urlcount, questionCount

# reading in jsons, reading column names, etc.
filename = "_keyword_1_natural_sciences.json"
directory= "data/filteredJSONs/"


"""load jsons + convert schema to needed format (authors, sources urls -> lists of strings,
simplifyTitle, unify authors to surnames in GS and Scopus; correct NoneType to string/ints)

"""

with open(str(directory+"MA"+filename)) as data_file:
    maJson = json.load(data_file)
    for doc in maJson:
        doc = unifySchema(doc)
        doc["_ - AA"] = SimplifyAuthorsInMA(doc["_ - AA"])
        doc["_ - Venue - FullName"] = str(doc["_ - Venue - FullName"] or "")
        doc["_ - Venue - Issue"] = str(doc["_ - Venue - Issue"] or "")
        doc["_ - Venue - Volume"] = str(doc["_ - Venue - Volume"] or "")


with open(str(directory+"scopus"+filename)) as data_file:
    scopusJson = json.load(data_file)
    for doc in scopusJson:
        doc = unifySchema(doc)
        doc["_ - AA"] = SimplifyAuthorsInScopus(doc["_ - AA"])
        doc["_ - Venue - Issue"] = str(doc["_ - Venue - Issue"] or "")
        doc["_ - Venue - Volume"] = str(doc["_ - Venue - Volume"] or "")
        doc["_ - Y"] = int(doc["_ - Y"][:4])
        doc["_ - CC"] = int(doc["_ - CC"])

with open(str(directory+"google_scholar"+filename)) as data_file:
    gsJson = json.load(data_file)
    for doc in gsJson:
        doc = unifySchema(doc)
        doc["_ - AA"] = SimplifyAuthorsInGoogleScholar(doc["_ - AA"])
        doc["_ - Y"] = int(doc["_ - Y"] or "0")
        doc["_ - CC"] = int(doc["_ - CC"] or "0")
        doc["_ - gsType"] = str(doc["_ - gsType"] or "none")


matchedDocs = []

#DOI matching: SCOPUS <-> MA, both sides
#(doicount, questionCountDOI)  = matchDOI (maJson, scopusJson, doicount)
#askForConfirmation ("finished matching DOIs, begin with URLs (GoogleScholar - MA)?", "", "", default="yes")
#(urlcount, questionCountURL) = matchURLs (maJson, gsJson, doicount)

(titlecount, questionCountTi) = matchURLs (maJson, scopusJson, titlecount)

#match DOIs -> scopus & MA; see if years similar and titles the same -> merge; otherwise - ask
                                                                                                    
