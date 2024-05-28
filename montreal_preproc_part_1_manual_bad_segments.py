#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:21:02 2023

@author: jan
"""

import mne
import numpy as np
# import matplotlib
# import statistics
from mne.preprocessing import create_ecg_epochs, create_eog_epochs

directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/whole_experience/'


fname = 'Montreal_05_2024-05-03_11-19-43.vhdr'

fnameEdited = fname[0:31]

rawData = mne.io.read_raw_brainvision(directory + fname, verbose='error',preload=True)

layout = np.loadtxt("standard_waveguard64.elc",delimiter="\t",dtype=str)
layout_electrodes = ["" for x in range(len(layout))]
for i in range(0,len(layout)):
    layout_electrodes[i] = layout[i,0][0:3]

layout = np.delete(layout, 0, 1)

for i in range(len(layout_electrodes)):
    if layout_electrodes[i][2]==' ':
        layout_electrodes[i] = layout_electrodes[i][0:2]

layoutFloat=np.zeros((len(layout[:,0]),len(layout[0,:])))

for i in range(0,len(layout[:,0])):
    for j in range(0,len(layout[0,:])):
        layoutFloat[i,j]=float(layout[i,j])
        
layoutBufferX = np.zeros(len(layoutFloat))

layoutBufferY = np.zeros(len(layoutFloat))            

layoutBufferX[:] = layoutFloat[:,0]

layoutBufferY[:] = layoutFloat[:,1]

layoutFloat[:,0] = layoutBufferY[:]

layoutFloat[:,1] = layoutBufferX[:]

layoutFloat[:,0] = layoutFloat[:,0]*-1

layout_dict = dict(enumerate(map(str, layout)))

for i in range(0,len(layout)):
    layout_dict[layout_electrodes[i]] = layoutFloat[i]
    del layout_dict[i]
    
montage = mne.channels.make_dig_montage(ch_pos=layout_dict)

montage.plot()
fig = montage.plot(kind="3d", show=False)  # 3D
fig = fig.gca().view_init(azim=70, elev=15)  # set view angle for tutorial

rawData.set_channel_types({'ECG': 'ecg'})
rawData.set_channel_types({'RESP3': 'resp'})
rawData.set_channel_types({'GSR4': 'gsr'})

# rawData.drop_channels(['RESP3', 'GSR4'])

rawData.set_montage(montage)

freqs = np.arange(60,320,60)
rawData.notch_filter(freqs=freqs)
# rawDataJourney.notch_filter(freqs=freqs)

rawData.filter(l_freq=0.5,h_freq=100.0,method="fir")

# rawData.filter(l_freq=0.1,h_freq=3.0,method="fir",picks=['GSR4'])

# rawDataJourney.filter(l_freq=0.01,h_freq=100.0,method="fir")
# rawDataJourney.filter(l_freq=0.01,h_freq=100.0,method="fir")
# annotations_load = mne.read_annotations("Montreal_01_2024-05-01_11-06-22_vhdr_annotations.fif", sfreq='auto', uint16_codec=None, encoding='utf8')

# rawDataBaseline.annotations = annotations_load
# rawDataBaseline.set_annotations(annotations_load)
eog_evoked = create_eog_epochs(rawData,ch_name='EOG').average()
eog_evoked.apply_baseline(baseline=(None, -0.2))
eog_evoked.plot_joint()

ecg_evoked = create_ecg_epochs(rawData,ch_name='ECG').average()
ecg_evoked.apply_baseline(baseline=(None, -0.2))
ecg_evoked.plot_joint()


rawData.plot()


# rawData.annotations.save(fnameEdited + "_vhdr_annotations.fif",overwrite=True)
