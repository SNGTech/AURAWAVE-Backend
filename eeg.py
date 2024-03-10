import mne
import numpy as np
import copy
import pandas as pd 
import math

class EEG:
    """
    Expected of raw_data json format
    {
        'Fp1': [1e-5, ..., 8e-4],
        'O1': [3e-4, ..., 6e-7],
        ...
        'Cz': [0, ..., 0]
    }
    """

    """
    Expected of profile_info json format
    {
        'Gender': 'M',
        'Age': 65
    }
    """

    def __init__(self, eeg_data, sfreq, profile_info):
        # Prepare data in MNE Data Format
        self.electrodes = eeg_data.keys()
        self.sfreq = sfreq
        self.raw_data = [x for x in eeg_data.values()]

        self.profile_info = profile_info

    def split_into_freq_bands(self, raw):
        iter_freqs = [("delta", 1, 3), ("theta", 4, 7), ("gamma", 30, 100), ("beta", 13, 30), ("alpha", 8, 12)]
        freq_map = []
        gfp_band_avg = []

        for band, l_freq, h_freq in iter_freqs:
            raw_copy = copy.deepcopy(raw)
            
            filtered = mne.filter.filter_data(raw_copy, self.sfreq, l_freq, h_freq, l_trans_bandwidth=1, h_trans_bandwidth=1, verbose=False)
            freq_map.append(((band, l_freq, h_freq), filtered))

        for (band, l_freq, h_freq), raw in freq_map:
            times = np.arange(0, raw.shape[1]) * (1/self.sfreq) * 1e3 # Convert to ms
            gfp = np.sum(raw ** 2, axis=0)
            print(raw[:, :5])
            print(gfp[:5])
            # print(times.shape)
            gfp = mne.baseline.rescale(gfp, times, baseline=(None, 0), verbose=False)

            gfp_band_avg.append((band, np.average(gfp).astype('float64')))

        return gfp_band_avg

    def prepare_data(self):
        df = pd.DataFrame({'Gender': [self.profile_info['Gender']], 'Age': [self.profile_info['Age']]})

        df['alpha'] = 0.0
        df['beta'] = 0.0
        df['gamma'] = 0.0
        df['theta'] = 0.0
        df['delta'] = 0.0
        # df['max_freq_band'] = ''
        
        freq_bands = self.split_into_freq_bands(self.raw_data)
        for band, gfp_avg in freq_bands:
            df.loc[0, band] = gfp_avg
        # self.data.loc[i, 'max_freq_band'] = freq_bands[np.argmax([x[1] for x in freq_bands])][0]

        print(df)
        return df

    def get_split_freqbands_json(self):
        freq_bands_json = {}
        freq_bands = self.split_into_freq_bands(self.raw_data)
        
        freqband_arr = []
        gfp_avg_arr = []
        for band, gfp_avg in freq_bands:
            freqband_arr.append(band)
            gfp_avg_arr.append(gfp_avg)
            freq_bands_json[band] = gfp_avg
        
        freq_bands_json['min_band'] = freqband_arr[np.argmin(gfp_avg_arr)]
        freq_bands_json['max_band'] = freqband_arr[np.argmax(gfp_avg_arr)]
        
        return freq_bands_json
        
    def get_metadata(self):
        metadata = {
            'n_pts_recorded': len(self.raw_data[0]),
            'sampling_rate': self.sfreq,
            'high_pass_freq': 1,
            'low_pass_freq': 100,
            'adc_vref': 5.08
        }

        return metadata
