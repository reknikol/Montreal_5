#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:21:02 2023

@author: jan
"""

import mne
import numpy as np



directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/Peak/'

# directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/Resting_state/baseline/'

fname = 'Montreal_10_2024-05-06_11-07-42.vhdr'

# fname = 'Montreal_01_2024-05-01_10-58-46.vhdr'

rawData = mne.io.read_raw_brainvision(directory + fname, verbose='error',preload=True)


freqs = np.arange(60,320,60)
rawData.notch_filter(freqs=freqs)

rawData.filter(l_freq=0.01,h_freq=100.0,method="fir")

rawData.filter(l_freq=0.01,h_freq=3.0,method="fir",picks=['GSR4'])

rawDataCopy = rawData.copy()

rawDataCopy.filter(l_freq=1.0,h_freq=30.0,method="fir",picks=['ECG'])


################# R detector from ECG QRS complex#################
ecgData = np.zeros(len(rawDataCopy._data[64]))

# polarity correction
if np.mean(rawDataCopy._data[64]) > 0:
    ecgData = rawDataCopy._data[64]*-1.0
else:
    ecgData = rawDataCopy._data[64]

detectSignal = np.zeros(len(ecgData))


for i in range(0,len(ecgData)):
    if i > 0 and i < len(ecgData):
        detectSignal[i]=np.power(ecgData[i]- ecgData[i-1],2)

#### quality signal regular check on 30 sec time windows####
detectSignalCheck30s = []
detectSignalCheck30sMean = []
iteration = 0
for i in range(0,len(detectSignal)):
    if iteration < (int(rawData.info['sfreq']*30)):
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
    if iterationLoop > (int(rawData.info['sfreq']*30)):
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
            if len(detectTimeCompressedBuffer)!=0:
                # print(detectTimeCompressedBuffer)
                detectTimeCompressed.append(int(np.mean(detectTimeCompressedBuffer)))
                detectTimeCompressedBuffer = []
RRtime = []            
if len(detectTimeCompressed) > 1:
    # RRtime = np.zeros(len(detectTimeCompressed)-1)
    for i in range(0,len(detectTimeCompressed)-1):
        # RRtime[i] = (detectTimeCompressed[i+1]-detectTimeCompressed[i])/rawData.info["sfreq"]
        if (detectTimeCompressed[i+1]-detectTimeCompressed[i])/rawData.info["sfreq"] < 2:
            RRtime.append((detectTimeCompressed[i+1]-detectTimeCompressed[i])/rawData.info["sfreq"])

    RRtimeMean = np.mean(RRtime)
    RRtimeStd = np.std(RRtime)
    RRtimeMax = np.max(RRtime)
    RRtimeMin = np.min(RRtime)
    rmssd = np.sqrt(np.mean(np.square(np.diff(RRtime))))
    
    print("RRtime :" + str(RRtimeMean) + " +- " +str(RRtimeStd))
    print("RRtime max: " +str(RRtimeMax) + " RRtime min: " + str(RRtimeMin))
    print("Mean HR rate: "+str(1/((RRtimeMean)/60)) + " bpm")
    print("HRV rmssd: " + str(rmssd))
else:
    print("Error in ECG QRS complex detection - less than two QRS detection")

# matplotlib.pyplot.boxplot(RRtime)

eventsECG = np.ones([len(detectTimeCompressed),3])
eventsECG[:,0] = detectTimeCompressed[:]

del rawDataCopy
##############################################################


############## GSR procesing #################################
gsrData = np.zeros(len(rawData._data[66]))
gsrData = rawData._data[66]
############## median detect #################################

# detectSignalGSRMedian = np.zeros(len(gsrData))
# detectSignalGSRMedianBuffer = []
# for i in range(0,len(gsrData)):
#     detectSignalGSRMedianBuffer.append(gsrData[i])
#     if i > 128 and i < len(gsrData):
#         detectSignalGSRMedian[i]= statistics.median(detectSignalGSRMedianBuffer)
#         # np.power(gsrData[i]- gsrData[i-512],4)


##################### dif detect method#######################

detectSignalGSR = np.zeros(len(gsrData))

for i in range(0,len(gsrData)):
    if i > 512 and i < len(gsrData):
        detectSignalGSR[i]=np.power(gsrData[i]- gsrData[i-512],4)
        
#### quality signal regular check on 30 sec time windows####
detectSignalCheck30sGSR = []
detectSignalCheck30sMeanGSR = []
iteration = 0
for i in range(0,len(detectSignalGSR)):
    if iteration < (int(rawData.info['sfreq']*30)):
        detectSignalCheck30sGSR.append(detectSignalGSR[i])
    else:
        # print(np.std(detectSignalCheck30s))
        detectSignalCheck30sMeanGSR.append(np.mean(detectSignalCheck30sGSR))
        iteration = 0
        detectSignalCheck30sGSR=[]
    iteration +=1
        
############################################################

# detectSignalGSRMean = np.mean(detectSignalGSR)
# detectTimeGSR = []
# for i in range(0,len(detectSignalGSR)):
#     if detectSignalGSR[i] > 1.5*detectSignalGSRMean:
#         # print("R detected")
#         countR += 1
#         detectTimeGSR.append(i)

###############new part witg windowed mean 30s############ start
iteration = 0
iterationLoop = 0
# detectSignalGSRMean = np.mean(detectSignalGSR)
detectTimeGSR = []
for i in range(0,len(detectSignalGSR)):
    # if detectSignal[i] > 4*detectSignalMean:
    iterationLoop += 1
    if iteration < len(detectSignalCheck30sMeanGSR):
        if detectSignalGSR[i] > 1.5*detectSignalCheck30sMeanGSR[iteration]:
            detectTimeGSR.append(i)
    else:
        if detectSignalGSR[i] > 5*detectSignalCheck30sMeanGSR[iteration-1]:
            detectTimeGSR.append(i)
    if iterationLoop > (int(rawData.info['sfreq']*30)):
        iteration += 1
        iterationLoop = 0
###############new part witg windowed mean 30s############ end

detectTimeGSRCompressed = []
detectTimeGSRCompressedBuffer = []

for i in range(0,len(detectTimeGSR)):
    if i>0:
        if (detectTimeGSR[i]-detectTimeGSR[i-1]) < 8*rawData.info['sfreq']:
            detectTimeGSRCompressedBuffer.append(detectTimeGSR[i])
        else:
            if len(detectTimeGSRCompressedBuffer) != 0:
                detectTimeGSRCompressed.append(int(np.mean(detectTimeGSRCompressedBuffer)))
                detectTimeGSRCompressedBuffer = []

eventsGSR = np.ones([len(detectTimeGSRCompressed),3])
eventsGSR[:,0] = detectTimeGSRCompressed[:]
eventsGSR[:,2] = 2
eventsGSR_intArray = eventsGSR.astype(int)

##############################################################


####concatanate events########################################
events = np.concatenate((eventsECG,eventsGSR),axis=0)
##############################################################

rawData.plot(events=eventsECG)

