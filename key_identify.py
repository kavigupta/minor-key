"""
Utilities for key identification
"""

import numpy as np

from fftutils import convert_to_note
from keys import Keys

PIANO_NOTES = np.array(["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"])

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
        out of the set of possible_keys, along with the score
    """
    cost_per_key_type = [[0] for _ in possible_keys]
    for chord in chords:
        for idx, key in enumerate(possible_keys):
            cost_per_key_type[idx].append(cost_per_key_type[idx][-1] + key.score_chord(chord))
    for time in range(len(chords)):
        best_index = max(range(len(possible_keys)),
                         key=lambda index, time=time: cost_per_key_type[index][time + 1])
        yield (possible_keys[best_index], cost_per_key_type[best_index][time + 1])

def best_key_for_chord_subsequences(chords, possible_keys):
    """
    Outputs a ragged list result where
        result[s][l - 1] == the highest score for chords[s:s + l]
    """
    return [list(best_key_for_chords_incremental(chords[s:], possible_keys))
            for s in range(len(chords))]

def best_multiple_keys_for_chords(chords, number_keys, possible_keys):
    """
    Outputs a Keys instance representing the best possible key series
                of length <= `possible_keys`
                for `chords`
    """
    current_keys = best_key_for_chord_subsequences(chords, possible_keys)
    overall = [Keys({})] * (len(chords) + 1)
    for _ in range(number_keys):
        overall = combine(overall, current_keys)
    return overall[-1]

def combine(prev_keys, current_keys):
    """
    prev_keys[t] == a Keys instance representing the best way to key chords[:t]
    current_keys[s][l - 1] == the best key for chords[s:s+l]

    Outputs: result where
        result[t] == a Keys instance representing the best way to key chords[:t]
    """
    return [Keys({})] + [
        max([prev_keys[start].additional((start, time), *current_keys[start][time-start-1])
             for start in range(time)],
            key=lambda x: x.score)
        for time in range(1, len(prev_keys))
    ]
