"""
Utilities for key identification
"""

import numpy as np

MIDDLE_C = 261.625565
PIANO_NOTES = np.array(["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"])

def convert_to_note(ffts, rate, fft_rate):
    """
    Convert the given index into an FFT array into a note value (12ths above middle C)

    ffts: the array of FFTs that the rate is indexed into, used only for its length
    rate: the rate that the original file was played at
    fft_rate: the index into ffts we are converting to a note
    """
    return 12 * np.log(rate / len(ffts) * (fft_rate + 0.01) / MIDDLE_C) / np.log(2)

def to_string(note):
    """
    Gets a string representation of a given note. For examples see TestNoteToString
    """
    return PIANO_NOTES[note % 12] + str(note // 12 + 4)

def get_notes(rate, clip, number_notes):
    """
    Get the top `number_notes` notes from the given sample.
    """
    freqs = np.fft.fft(clip)
    indices = np.argsort(-np.abs(freqs)[:len(freqs)//2])
    notes = np.round(convert_to_note(freqs, rate, indices))
    uniques = set()
    for note in notes:
        if note not in uniques:
            uniques.add(int(note))
        if len(uniques) == number_notes:
            break
    return uniques
