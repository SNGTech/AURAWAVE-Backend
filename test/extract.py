import os

import numpy as np
import mne
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, find_matching_paths
import os.path as op
import matplotlib.pyplot as plt

class EEGExtract():
    def __init__(self, dataset: str, subject: str):
        bids_root = f'./{dataset}'
        task = "eyesclosed"
        suffix = "eeg"

        bids_paths = find_matching_paths(
            bids_root, datatypes='eeg', sessions=None, extensions=['set']
        )
        bids_path = bids_paths[0].update(subject=subject, task=task, suffix=suffix)
        self.raw = read_raw_bids(bids_path=bids_path, verbose=True)

        self.sampling_freq = self.raw.info['sfreq']
        self.sampling_rate = 1 / self.sampling_freq * 1000

    def extract(self, channel, start, stop):
        print("Sampling Rate: %.2fms" % (self.sampling_rate))

        start_stop_seconds = np.array([start, stop])
        start_sample, stop_sample = (start_stop_seconds * self.sampling_freq).astype(int)

        return self.raw[channel, start_sample:stop_sample]
