#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:21:02 2023

@author: jan
"""

import mne
import os
import numpy as np
import csv






class dataset:
    
    def __init__(self,fname,directory,filterL,filterH,rawData,RRtimeMean,RRtimeStd,RRtimeMax,RRtimeMin,rawDataCopy,rmssd):
        
        self.fname = fname
        self.directory = directory
        self.filterL = filterL
        self.filterH = filterH
        self.rawData = rawData
        self.RRtimeMean = RRtimeMean
        self.RRtimeStd = RRtimeStd
        self.RRtimeMax = RRtimeMax
        self.RRtimeMin = RRtimeMin
        self.rawDataCopy = rawDataCopy
        self.rmssd = rmssd
        
    def loadData(self):
        
        self.rawData = mne.io.read_raw_brainvision(self.directory + self.fname, verbose='error',preload=True)
        return self.fname
        
    def filterData(self):
        freqs = np.arange(60,320,60)
        self.rawData.notch_filter(freqs=freqs)

        # self.rawData.filter(l_freq=0.01,h_freq=100.0,method="fir")

        # self.rawData.filter(l_freq=0.01,h_freq=3.0,method="fir",picks=['GSR4'])

        self.rawDataCopy = self.rawData.copy()

        self.rawDataCopy.filter(l_freq=self.filterL,h_freq=self.filterH,method="fir",picks=['ECG'])
        
    def HRVpipeline(self):
        
        ecgData = np.zeros(len(self.rawDataCopy._data[64]))

        # polarity correction
        if np.mean(self.rawDataCopy._data[64]) > 0:
            ecgData = self.rawDataCopy._data[64]*-1.0
        else:
            ecgData = self.rawDataCopy._data[64]

        detectSignal = np.zeros(len(ecgData))


        for i in range(0,len(ecgData)):
            if i > 0 and i < len(ecgData):
                detectSignal[i]=np.power(ecgData[i]- ecgData[i-1],2)

        #### quality signal regular check on 30 sec time windows####
        detectSignalCheck30s = []
        detectSignalCheck30sMean = []
        iteration = 0
        for i in range(0,len(detectSignal)):
            if iteration < (int(self.rawData.info['sfreq']*30)):
                detectSignalCheck30s.append(detectSignal[i])
            else:
                # print(np.std(detectSignalCheck30s))
                detectSignalCheck30sMean.append(np.mean(detectSignalCheck30s))
                iteration = 0
                detectSignalCheck30s=[]
            iteration +=1
                
        ############################################################
        detectSignalMean = np.mean(detectSignal)
        countR = 0
        detectTime = []
        iteration = 0
        iterationLoop = 0
        for i in range(0,len(detectSignal)):
            # if detectSignal[i] > 4*detectSignalMean:
            iterationLoop += 1
            if iteration < len(detectSignalCheck30sMean):
                if detectSignal[i] > 5*detectSignalCheck30sMean[iteration]:
                    # print("R detected")
                    countR += 1
                    detectTime.append(i)
            else:
                if detectSignal[i] > 5*detectSignalCheck30sMean[iteration-1]:
                    # print("R detected")
                    countR += 1
                    detectTime.append(i)
            if iterationLoop > (int(self.rawData.info['sfreq']*30)):
                iteration += 1
                iterationLoop = 0

        # for i in range(0,len(detectSignal)):
        #     if detectSignal[i] > 4*detectSignalMean:
        #         countR += 1
        #         detectTime.append(i)

                

        detectTimeCompressed = []
        detectTimeCompressedBuffer = []
        for i in range(0,len(detectTime)):
            if i>0:
                if (detectTime[i]-detectTime[i-1]) < 300:
                    detectTimeCompressedBuffer.append(detectTime[i])
                else:
                    # print(detectTimeCompressedBuffer)
                    if len(detectTimeCompressedBuffer)!=0:
                        detectTimeCompressed.append(int(np.mean(detectTimeCompressedBuffer)))
                        detectTimeCompressedBuffer = []
        RRtime = []            
        if len(detectTimeCompressed) > 1:
            # RRtime = np.zeros(len(detectTimeCompressed)-1)
            for i in range(0,len(detectTimeCompressed)-1):
                # RRtime[i] = (detectTimeCompressed[i+1]-detectTimeCompressed[i])/self.rawData.info["sfreq"]
                if (detectTimeCompressed[i+1]-detectTimeCompressed[i])/self.rawData.info["sfreq"] < 2:
                    RRtime.append((detectTimeCompressed[i+1]-detectTimeCompressed[i])/self.rawData.info["sfreq"])
                
            self.RRtimeMean = np.mean(RRtime)
            self.RRtimeStd = np.std(RRtime)
            self.RRtimeMax = np.max(RRtime)
            self.RRtimeMin = np.min(RRtime)
            self.rmssd = np.sqrt(np.mean(np.square(np.diff(RRtime))))
            print(self.RRtimeStd)
            
            # print("RRtime :" + str(RRtimeMean) + " +- " +str(RRtimeStd))
            # print("RRtime max: " +str(RRtimeMax) + " RRtime min: " + str(RRtimeMin))
            # print("Mean HR rate: "+str(1/((RRtimeMean)/60)) + " bpm")
            
        else:
            print("Error in ECG QRS complex detection - less than two QRS detection")

        # matplotlib.pyplot.boxplot(RRtime)

        eventsECG = np.ones([len(detectTimeCompressed),3])
        eventsECG[:,0] = detectTimeCompressed[:]

        # return RRtimeMean,RRtimeStd,RRtimeMax,RRtimeMin,heartRate
   
    def returnRRtimeMean(self):
        return self.RRtimeMean
    def returnRRtimeStd(self):
        print(self.RRtimeStd)
        return self.RRtimeStd
    def returnRRtimeMax(self):
        return self.RRtimeMax
    def returnRRtimeMin(self):
        return self.RRtimeMin
    
    def returnHeartRate(self):
        heartRate = 1/((self.RRtimeMean)/60)
        return heartRate
    def returnHRV(self):    
        return self.rmssd
        

        
# directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/Peak/'
directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/Resting_state/baseline/'




f = open('HRV_baseline_montreal.csv', 'w', encoding='UTF8', newline='')
writer = csv.writer(f)
fieldnames = ['datasetName','RRtimeMean',
              'RRtimeStd','RRtimeMax',
              'RRtimeMin','heartRate','HRV_rmssd']
writer = csv.DictWriter(f, fieldnames=fieldnames)
writer.writeheader()

dataBuffer= []

for filename in os.listdir(directory):
    if filename.endswith(".vhdr"):
        data = dataset(filename,directory,1.0,30.0,1,1,1,1,1,1,1)
        filename = data.loadData()
        print("-------------------")
        print(filename)
        print("-------------------")
        data.filterData()
        data.HRVpipeline()
        rows = [
                {'datasetName': filename,
                 'RRtimeMean': data.returnRRtimeMean(),
                 'RRtimeStd': data.returnRRtimeStd(),
                 'RRtimeMax': data.returnRRtimeMax(),
                 'RRtimeMin': data.returnRRtimeMin(),
                 'heartRate': data.returnHeartRate(),
                 'HRV_rmssd': data.returnHRV()
                 }
        ]
        writer.writerows(rows)
f.close()

       
        
# np.save('MontrealAfterRestingState', psdArrays, allow_pickle=True, fix_imports=True)


