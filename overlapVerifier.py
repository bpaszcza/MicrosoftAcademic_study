# -*- coding: utf-8 -*-
"""
Created on Thu May 25 15:06:50 2017

@author: bartosz
"""

#remove duplicate entries (the same except maybe for logprob)

#filter to filter out repeating documents in GS/Scopus/MA (and count those, obviously)

#function taking a list and finding ID's of the same docs or similar in other databases 



from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

#take the microsoft's list

#match entries from scopus to microsoft -> find coverage

#repeat for Scopus, GS list, EXCLUDING those already matched!!!