"""

"""

import time

import pynput
import numpy as np
import pandas as pd
import scipy

from blowboard import config as cfg


def classify_spectro_df(spectro_df: pd.DataFrame):
    """Take a spectrogram df and classify it as inputs."""

    # This checks if there's a peak characteristic of a whistle.
    def get_prominence(series):
        return scipy.signal.peak_prominences(series, [series.argmax()])[0][0]

    # Make a DataFrame to hold information we're going to use to classify what
    #  this audio means.
    df = pd.DataFrame(
        data=spectro_df.idxmax(),
        columns=['peak_freq'],
    )
    df['log_peak_freq'] = np.log(df.peak_freq)
    df['prominence'] = spectro_df.apply(get_prominence)
    df['whistle'] = df.prominence > cfg['prominence_threshold']

    # Get the regions where there's whistling to parse them
    active_regions = _get_active_regions(df)
    for start, end in active_regions:
        print(f'whistle detected: ({start}, {end})')
        keyboard = pynput.keyboard.Controller()
        keyboard.press('L')
        time.sleep(0.2)
        keyboard.release('L')


    # Drop anything which has been classified
    if active_regions:
        spectro_df = spectro_df.loc[:, active_regions[-1][-1]:]

    return spectro_df, df, active_regions

def _get_active_regions(df):
    """Get the regions of the DataFrame where there's acceptable whistle
    input."""

    # Retrieve contiguous regions of whistling
    whistle_regions = []
    region_start = None
    for time in df.index:
        if region_start and not df.whistle[time]:
            # We're in a region but it's not silent
            #  so end the region, not inclusive.
            whistle_regions.append((region_start, time))
            region_start = None
        if not region_start and df.whistle[time]:
            # We're not in a region, and it's silent,
            #  so make a new region
            region_start = time

    CONCAT_TIME = 0.1  # seconds
    concat_regions = []
    if len(whistle_regions) >= 2:
        prev_start, prev_end = whistle_regions[0]
        for start, end in whistle_regions:
            if prev_end + CONCAT_TIME > start:
                prev_end = end
            else:
                concat_regions.append((prev_start, prev_end))
                prev_start = start
                prev_end = end
        concat_regions.append((prev_start, prev_end))

    MIN_WHISTLE_TIME = 1  # seconds
    active_regions = []
    for start, end in concat_regions:
        if end - start > MIN_WHISTLE_TIME:
            active_regions.append((start, end))

    return active_regions
