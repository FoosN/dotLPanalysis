#!/usr/bin/env python
# -*-coding:Utf-8 -*
"""
Created on Tue Apr  8 16:53:03 2014
Copyright (c) 2014, Nicolas Foos
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/
or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.

"""
""" programm to plot SigAno, R-meas, CC(1/2) AnomalCorr vs Resolution through
different XSCALE file """

import time
import sys
import os
import re
import numpy as np
import matplotlib.pyplot as pp
import pickle

USAGE = """ USAGE: %s [OPTION]... FILES
 
FILES is one or more XSCALE.LP file """


resultFile = raw_input ('give name for result file, default is : result.' \
+str(time.time())+ ' :')
if resultFile == '' :
    resultFile = "result."+ str(time.time())
try:
    os.makedirs(resultFile, 0777)
except OSError, e:
     print 'WARNING : Problem to create Directory for results'
     if not "File exists" in e:
       exit(0)

          
maninput_files = []
for arg in sys.argv[1:]:
    try:
        if os.path.isfile(arg):
            f = open(arg)
            lines = f.readlines()
            f.close()
            if ("***** XSCALE *****" in lines[1]) and \
               ("elapsed wall-clock time" in lines[-1]):
                maninput_files.append(arg)
            elif ("***** CORRECT *****" in lines[1]) and \
               ("elapsed wall-clock time" in lines[-1]):
                 maninput_files.append(arg)  
    except: 
        pass




class dataset:
    """contain information about data used : file path, 
    type of file (output xscale or CORRECT from xds), table with value,
    column name for the table"""
    
    def __init__(self, input_file):
        self.path = input_file
        self.dataType = ''
        self.text = ''
        self.table = []
        self.colName = ['Resolution Limit', 'number of observed reflection'
            , 'number of unique reflection', 'number ofpossible reflection', 
            'completness of Data', 'R-factor obs', 'R-factor expect', 'Compared'
            , 'IoverSig', 'R-meas', 'CC(half)', 'Anom_Corr', 'SigAno', 'Nano']
        self.dico = {}    
        try:
            f = open(self.path)
            self.text = f.read()
            f.close()
        except e:
            print "Can't open file %s." % self.path
            raise e
        if ("***** XSCALE *****" in self.text[:200]) and \
               ("elapsed wall-clock time" in self.text[-100:]):
            self.dataType = 'XSCALE'
            textstart = ' RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  CC(1/2)  Anomal  SigAno   Nano\n'
            textend = ' ========== STATISTICS OF INPUT DATA SET ==========\n'
        
        elif ("***** CORRECT *****" in self.text[:200]) and \
               ("elapsed wall-clock time" in self.text[-100:]):
            self.dataType = 'CORRECT'        
            textstart = ' RESOLUTION     NUMBER OF REFLECTIONS    COMPLETENESS R-FACTOR  R-FACTOR COMPARED I/SIGMA   R-meas  CC(1/2)  Anomal  SigAno   Nano\n'
            textend = ' NUMBER OF REFLECTIONS IN SELECTED SUBSET OF IMAGES' 
        
        
        def _findCorrectionFactImgNbr():
            with open(self.path) as f1:
                lines = f1.readlines()
                for line in lines:
                    if re.findall(r"CORRECTION FACTORS AS FUNCTION OF IMAGE NUMBER & RESOLUTION", line):
                        nbrOfCorr = lines[(lines.index(line)+7)]
                        self.dico["nbrOfCorr"] = nbrOfCorr.split()[-1]
                        freedomChisq = lines[(lines.index(line)+8)]
                        self.dico["freedomChisq"] = freedomChisq.split()[-1]
                        ChisqOfFitOfCorr = lines[(lines.index(line)+9)]
                        self.dico["ChisqOfFitOfCorr"] = ChisqOfFitOfCorr.split()[-1]
                        nbrOfReflct = lines[(lines.index(line)+15)]
                        self.dico["nbrOfReflct"] = nbrOfReflct.split()[-1]
#                with open("donnees", "wb") as fichier:
#                    mon_pickler = pickle.Pickler(fichier)
#                    mon_pickler.dump(self.dico)
        _findCorrectionFactImgNbr()
        
        #def __repr__(self):
        #    return  
        def _parse_XSCALE():
            f = open(self.path)
            lines = f.readlines()
            f.close()
            for k, line in enumerate(lines):
               if line == textstart:
                    linestart = k
               if line.startswith(textend):     
                    lineend = k
#cleaning the table to keep only value not str.
            interest = lines[linestart:lineend]
            interclean = interest[3:-3] # donne une liste propre
            intercleanstr = ''.join(interclean)
            intercleanstr = intercleanstr.replace("%", '')
            intercleanstr = intercleanstr.replace("*", '')
            intercleanstr = intercleanstr.replace("\n", '')
            interest = intercleanstr.split()
            interest2 = []
            for value in interest:
                interest2.append(float(value))
            table1 = np.reshape(np.array(interest2), (-1, 14))
            self.table = table1.swapaxes(0,1)
            #print table2
            #table3 = np.fliplr(table2)
            #print "c'est table3" 
            #print table3
            #self.table = table3

        _parse_XSCALE()

###############################################
#def findCorrectionFactImgNbr(dictioEntry, inputFile):
    

#    for lines in inputFile:
#        if re.findall(r"CORRECTION FACTORS AS FUNCTION OF IMAGE NUMBER & RESOLUTION", lines):
#            nbrOfCorr = inputFile[(inputFile.index(lines)+7)]
#            nbrOfCorr = nbrOfCorr.split()[-1]
#            freedomChisq = inputFile[(inputFile.index(lines)+8)]
 #           freedomChisq = freedomChisq.split()[-1]
 #           ChisqOfFitOfCorr = inputFile[(inputFile.index(lines)+9)]
 #           ChisqOfFitOfCorr = ChisqOfFitOfCorr.split()[-1]
 #           nbrOfReflct = inputFile[(inputFile.index(lines)+15)]
 #           nbrOfReflct = nbrOfReflct.split()[-1]
 #           return freedomChisq
#            return ChisqOfFitOfCorr
#            return nbrOfReflct
            
        ###############################################

def plotData(colXnmbr, colYnmbr, colYname, datasets):
        pp.clf()
        i = 0
        legends = []
        while i <= len(datasets)-1:
            pp.xlim((max(datasets[i].table[colXnmbr]),min(datasets[i].table[colXnmbr]-1)))
            pp.plot(datasets[i].table[colXnmbr], datasets[i].table[colYnmbr])
            legends.append([datasets[i].path])
            i+=1
        #print max(datasets[i].table[colXnmbr])
        #print min(datasets[i].table[colXnmbr])   
        ticks = np.arange(int(min(datasets[i-1].table[colXnmbr])), int(max(datasets[i-1].table[colXnmbr])), 1)
        
        #ticks = np.arange(2, 12, 2) 
        #ticks = (datasets[i-1].table[colXnmbr])
        #ticks = ticks[::-1]
        ticks = ticks.tolist()
        ticks.reverse()
        index2remove = [-2, -1]
        for index in index2remove:
            del ticks[index]
        ticks.append(round(min(datasets[i-1].table[colXnmbr]),1))
        
        #newTicks=[]
        #for i in ticks:
         #   while i < len(ticks):
          #      print i
           #     i +=1
            #    newTicks.append(int(i))
        #print newTicks
        #ticks.pop(-1)
        #ticks.pop(-1)
        #ticks =         
        #print ticks
        #minAbsciss = min(datasets[i-1].table[colXnmbr])
        #print minAbsciss
        labels = ticks
        print ticks
        print type(ticks)
        #print labels
        pp.xticks(ticks, labels)       
        pp.legend(legends, loc= 'best', prop={'size':8})
        pp.xlabel("Resolution Angstrom")
        pp.ylabel(datasets[0].colName[colYname])
        pp.savefig(os.path.join(resultFile, datasets[0].colName[colYname]+ '.png'),
        dpi=600, facecolor='w', edgecolor='w', orientation='landscape')
        pp.figure()
        pp.plot()
        pp.close()
            

def writeCorreParams(datasets):
    outputfile = open(os.path.join(resultFile, "SummaryCorrParams.log"), 'a')
    outputfile.write(20*"*"+" Correction Parameters Summary " + 20*"*"+ "\n" +"datasets : " + str(datasets.path))
    for (info, value) in datasets.dico.items():
        info = ("parameters : {} is {} \n".format(info, value))
        outputlog = (info)
        outputfile.write(outputlog)
    print datasets.dico    
    outputfile.close()

############### COMMAND to make the JOB #####################

listedata = []
for i in maninput_files:
    listedata.append(dataset(i)) 
interestingCol = [8, 9, 10, 11, 12, 13]
for i in listedata:
    writeCorreParams(i)
    for i in interestingCol:
        plotData(0, i, i, listedata)
    
