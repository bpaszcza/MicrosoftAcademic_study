# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 09:43:11 2017

@author: bartosz
"""

from pathlib import Path
import json
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go

#google scholar function to unify schema!!!! omitting [CITATION] in Google Scholar -> 

def googleScholarSchemaUnifier (json_data):
    outputContent = []
    #shortening output - removing abstract, bag-of-words, list of sources
    for element in json_data:
        #print (element)
        #create new element which is to have unified schema
        if 'type' not in element or element['type'] != 'CITATION':
            shortenedEntity = {}
            if 'authors' in element: shortenedEntity['AA'] = element['authors']
            if 'cites' in element: shortenedEntity['CC'] = element['cites']
            if 'title' in element: shortenedEntity['Ti'] = element['title']
            if 'source' in element: shortenedEntity['Venue'] = element['source']
            if 'year' in element: shortenedEntity['Y'] = element['year']
            outputContent.append(shortenedEntity)
            
    return(outputContent)


def basicStatistics(queryPhrase):
    #take in data from files (conditional if exists)
    #queryPhrase = 'CP invariance' #Ti
    outputFileName = queryPhrase.replace(" ", "_")
    dataDictionary = {}

    maFile = str('data/MA_bytitle_%s.json' % outputFileName)
    maFilePath = Path(maFile)
    if maFilePath.is_file():
        # file exists
        with open(maFile) as json_data:
            #load json data
            microsoftAcademicData = json.load(json_data)
            dataDictionary['microsoftAcademic'] = microsoftAcademicData
    
    scopusFile = str('data/scopus_bytitle_%s.json' % outputFileName)
    scopusFilePath = Path(scopusFile)
    if scopusFilePath.is_file():
        # file exists
        with open(scopusFile) as json_data:
            #load json data
            scopusData = json.load(json_data)
            dataDictionary['scopus'] = scopusData
    
    googleScholarFile = str('data/googlescholar_bytitle_%s.json' % outputFileName)
    googleScholarPath = Path(googleScholarFile)
    if googleScholarPath.is_file():
        # file exists
        with open(googleScholarFile, encoding="utf8") as json_data:
            #load json data
            googleScholarData = json.load(json_data)
            
            #normalise Google Scholar Data
            googleScholarData = googleScholarSchemaUnifier(googleScholarData)
            dataDictionary['googleScholar'] = googleScholarData
            
    webOfScienceFile = str('data/webofscience_bytitle_%s.json' % outputFileName)
    webOfSciencePath = Path(webOfScienceFile)
    if webOfSciencePath.is_file():
        # file exists
        with open(webOfScienceFile, encoding="utf8") as json_data:
            #load json data
            webOfScienceData = json.load(json_data)
            dataDictionary['webOfScience'] = webOfScienceData
    
    
    
    #sum number of entities (papers),  sum number of citations
    statistics = {}
    statistics['query'] = queryPhrase
    #vis number of papers in each (including WoS)
    def countPapers (statistics):
        papersCount = {}
        #iterate through datasets in dictionary
        for key, dataset in dataDictionary.items():
            papersCount[key] = len(dataset)
            
        statistics['papersCount'] = papersCount
        return(statistics)
    
    def countCitations (statistics):
        citationCount = {}
        
        #iterate through datasets in dictionary
        for key, dataset in dataDictionary.items():
            count = 0
            for document in dataset:
                if 'CC' in document: count = count + int(document['CC'])
            citationCount[key] = count
        statistics['citationCount'] = citationCount
        return(statistics)
    
    def missingValues (statistics):
        missingCitationCount = {}
        #iterate through datasets in dictionary
        for key, dataset in dataDictionary.items():
            count = 0
            for document in dataset:
                if 'CC' not in document: count = count + 1
            missingCitationCount[key] = count
        statistics['missingCitationCount'] = missingCitationCount
        
        missingYearCount = {}
        for key, dataset in dataDictionary.items():
            count = 0
            for document in dataset:
                if 'Y' not in document: count = count + 1
            missingYearCount[key] = count
        statistics['missingYearCount'] = missingYearCount
        
        return(statistics)
    
    
    statistics = countPapers(statistics)
    statistics = countCitations(statistics)
    #vis number of citations in each
    papersPlot = go.Bar(
                x=list(statistics['papersCount'].keys()),
                y=list(statistics['papersCount'].values())
        )
    
    citationPlot = go.Bar(
                x=list(statistics['citationCount'].keys()),
                y=list(statistics['citationCount'].values())
        )
    
    #py.plot(data, filename='Total number of citations to document with phrase %s in title' % queryPhrase)
    
    fig = tools.make_subplots(rows=1, cols=2, subplot_titles=('Number of documents', 'Total number of citations of documents found'))
    
    fig.append_trace(papersPlot, 1, 1)
    fig.append_trace(citationPlot, 1, 2)
    
    fig['layout'].update(height=600, width=800, title="""No of documents and citations for documents with phrase '%s' in title""" % queryPhrase, showlegend=False)
    plot_url = py.plot(fig, filename='MA_study query by title %s' % queryPhrase)
    
    #basic stats on #docs without citation, citation distro histograms, std dev?
def advancedStats (queryPhrase):
    
    
    
    
    
    trace1 = go.Bar(
    x=['giraffes', 'orangutans', 'monkeys'],
    y=[20, 14, 23],
    name='SF Zoo'
    )
    trace2 = go.Bar(
        x=['giraffes', 'orangutans', 'monkeys'],
        y=[12, 18, 29],
        name='LA Zoo'
    )
    
    data = [trace1, trace2]
    layout = go.Layout(
        barmode='group'
    )
    
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='grouped-bar')