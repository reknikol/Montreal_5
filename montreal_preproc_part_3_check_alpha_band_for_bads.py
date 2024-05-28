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


directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/Peak/'


fname = 'Montreal_05_2024-05-03_11-19-43'

fnameEdited = fname[0:31]

data = mne.io.read_raw(directory + fname + "_ICA_eog_bad_ch_Interpolated.fif", verbose='error',preload=True)

# layout = np.loadtxt("standard_waveguard64.elc",delimiter="\t",dtype=str)
# layout_electrodes = ["" for x in range(len(layout))]
# for i in range(0,len(layout)):
#     layout_electrodes[i] = layout[i,0][0:3]

# layout = np.delete(layout, 0, 1)

# for i in range(len(layout_electrodes)):
#     if layout_electrodes[i][2]==' ':
#         layout_electrodes[i] = layout_electrodes[i][0:2]

# layoutFloat=np.zeros((len(layout[:,0]),len(layout[0,:])))

# for i in range(0,len(layout[:,0])):
#     for j in range(0,len(layout[0,:])):
#         layoutFloat[i,j]=float(layout[i,j])
        


# layout_dict = dict(enumerate(map(str, layout)))

# for i in range(0,len(layout)):
#     layout_dict[layout_electrodes[i]] = layoutFloat[i]
#     del layout_dict[i]
    
# montage = mne.channels.make_dig_montage(ch_pos=layout_dict)



# rawData.set_channel_types({'ECG': 'ecg'})
# rawData.set_channel_types({'ECG': 'resp'})
# rawData.set_channel_types({'GSR4': 'gsr'})

freqs = np.arange(60,320,60)
data.notch_filter(freqs=freqs)
# rawDataJourney.notch_filter(freqs=freqs)

data.filter(l_freq=8.0,h_freq=12.0,method="fir")

data.filter(l_freq=0.1,h_freq=3.0,method="fir",picks=['GSR4'])

# rawDataJourney.filter(l_freq=0.01,h_freq=100.0,method="fir")
# rawDataJourney.filter(l_freq=0.01,h_freq=100.0,method="fir")
# annotations_load = mne.read_annotations("Montreal_01_2024-05-01_11-06-22_vhdr_annotations.fif", sfreq='auto', uint16_codec=None, encoding='utf8')

# rawDataBaseline.annotations = annotations_load
# rawDataBaseline.set_annotations(annotations_load)
data.plot()

# data.annotations.save(fnameEdited + "_vhdr_annotations.fif",overwrite=True)
