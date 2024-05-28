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
from mne.preprocessing import ICA, corrmap, create_ecg_epochs, create_eog_epochs

################################################################################
#Before running the script:
# edit bad_channels which holds list of bad channels

#script will load data + data annotations, import layout and create montage,bad channel interpolation ,set the non-eeg channels, create eog and ecg epochs than, perform
# ICA and automaticaly repair the signal with EOG channel with ICA

################################################################################

directory = '/media/jan/ATiN_archive/JH_workspace/Montreal_exp/Peak/'

bad_channels = ['C2']


fname = 'Montreal_05_2024-05-03_11-19-43.vhdr'

fnameEdited = fname[0:31]


rawData = mne.io.read_raw_brainvision(directory + fname, verbose='error',preload=True)
# rawData.annotations = annotations_load
annotations_load = mne.read_annotations(fnameEdited + "_vhdr_annotations.fif", sfreq='auto', uint16_codec=None, encoding='utf8')

rawData.set_annotations(annotations_load)


layout = np.loadtxt("standard_waveguard64.elc",delimiter="\t",dtype=str)
layout_electrodes = ["" for x in range(len(layout))]
for i in range(0,len(layout)):
    layout_electrodes[i] = layout[i,0][0:3]
    # if len(layout[i,0]) == 4:
    #     layout_electrodes[i] = layout[i,0][0:3]
    # if len(layout[i,0]) == 3:
    #     layout_electrodes[i] = layout[i,0][0:2]
layout = np.delete(layout, 0, 1)

for i in range(len(layout_electrodes)):
    if layout_electrodes[i][2]==' ':
        layout_electrodes[i] = layout_electrodes[i][0:2]

layoutFloat=np.zeros((len(layout[:,0]),len(layout[0,:])))

for i in range(0,len(layout[:,0])):
    for j in range(0,len(layout[0,:])):
        layoutFloat[i,j]=float(layout[i,j])
        
# standard_waveguard64.elc
# layout[:,4]=str(0)
# layout = np.ones((64,4))
# a = np.array([23,34,23,45,23])

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
    # layout_dict[layout_electrodes[i]]
    del layout_dict[i]
    
montage = mne.channels.make_dig_montage(ch_pos=layout_dict)

# rawData.set_channel_types({'EOG': 'eog'})

rawData.set_channel_types({'ECG': 'ecg'})
rawData.set_channel_types({'RESP3': 'resp'})
rawData.set_channel_types({'GSR4': 'gsr'})


# rawData.drop_channels(['RESP3', 'GSR4'])

rawData.set_montage(montage)

# mne.channels.make_dig_montage(ch_pos=None, nasion=None, lpa=None, rpa=None, hsp=None, hpi=None, coord_frame='unknown')

freqs = np.arange(60,320,60)
rawData.notch_filter(freqs=freqs)
# rawDataJourney.notch_filter(freqs=freqs)

rawData.filter(l_freq=0.5,h_freq=100.0,method="fir")

rawData.info["bads"] = bad_channels
rawData.interpolate_bads(reset_bads=True, mode='accurate', origin='auto', method=None, exclude=(), verbose=None)

# rawData.filter(l_freq=0.1,h_freq=3.0,method="fir",picks=['GSR4'])

eog_evoked = create_eog_epochs(rawData,ch_name='EOG').average()
eog_evoked.apply_baseline(baseline=(None, -0.2))
eog_evoked.plot_joint()

ecg_evoked = create_ecg_epochs(rawData,ch_name='ECG').average()
ecg_evoked.apply_baseline(baseline=(None, -0.2))
ecg_evoked.plot_joint()

ICAInst = mne.preprocessing.ICA(n_components=35, noise_cov=None, random_state=None, method='fastica', fit_params=None, max_iter='auto', allow_ref_meg=False, verbose=None)
ICAInst.fit(rawData,reject_by_annotation=True)


explained_var_ratio = ICAInst.get_explained_variance_ratio(rawData)
for channel_type, ratio in explained_var_ratio.items():
    print(f"Fraction of {channel_type} variance explained by all components: {ratio}")

explained_var_ratio = ICAInst.get_explained_variance_ratio(
    rawData, components=[0], ch_type="eeg")

ratio_percent = round(100 * explained_var_ratio["eeg"])
print(
    f"Fraction of variance in EEG signal explained by first component: "
    f"{ratio_percent}%"
)



ICAInst.plot_sources(rawData)
ICAInst.plot_components()


# Using an EOG channel to select ICA components

eog_indices, eog_scores = ICAInst.find_bads_eog(rawData,ch_name='EOG')
ICAInst.exclude = eog_indices

rawDataReconstructed = rawData.copy()

ICAInst.plot_scores(eog_scores)
ICAInst.apply(rawDataReconstructed)

# rawDataReconstructed.save(directory + fnameEdited + "_ICA_eog_bad_ch_Interpolated.fif")
