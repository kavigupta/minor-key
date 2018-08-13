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

def by_chunk(rate, data, number_notes, chunk_size):
    """
    Get
        the top `number_notes` notes
        from each sample of length `chunk_size` seconds segment
        in the clip `data`
        with rate `rate`
    """
    chunk_size_indices = int(rate * chunk_size)
    for starting_idx in range(0, len(data), chunk_size_indices):
        yield get_notes(rate, data[starting_idx:starting_idx+chunk_size_indices], number_notes)

def best_key_for_chords_incremental(chords, possible_keys):
    """
    Gets key with the highest score for chords[:t] for every t from 1..len(chords)
        out of the set of possible_keys
    """
    cost_per_key_type = [[0] for _ in possible_keys]
    for chord in chords:
        for idx, key in enumerate(possible_keys):
            cost_per_key_type[idx].append(cost_per_key_type[idx][-1] + key.score_chord(chord))
    for time in range(len(chords)):
        best_index = max(range(len(possible_keys)),
                         key=lambda index, time=time: cost_per_key_type[index][time + 1])
        yield (possible_keys[best_index], cost_per_key_type[best_index][time + 1])
