"""
Utilities for converting to and from fft indices
"""

import numpy as np

MIDDLE_C = 261.625565

def convert_to_note(ffts, rate, fft_rate):
    """
    Convert the given index into an FFT array into a note value (12ths above middle C)

    ffts: the array of FFTs that the rate is indexed into, used only for its length
    rate: the rate that the original file was played at
    fft_rate: the index into ffts we are converting to a note
    """
    return 12 * np.log(rate / len(ffts) * (fft_rate + 0.01) / MIDDLE_C) / np.log(2)
