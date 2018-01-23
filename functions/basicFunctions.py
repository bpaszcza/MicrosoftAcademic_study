# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 13:58:04 2017

@author: bartosz
"""

# basic functions used in code


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