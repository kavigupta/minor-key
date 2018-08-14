
import numpy as np

from key_identify import best_multiple_keys_for_chords, by_chunk
from keys import ALL_MAJORS_MINORS, major, minor
from transform import Identity

def minor_key(data, rate, key_transform, number_notes, number_keys, chunk_size, possible_keys=ALL_MAJORS_MINORS):
    keys = best_multiple_keys_for_chords(
        list(by_chunk(rate, data, number_notes, chunk_size)),
        number_keys,
        possible_keys
    )
    result = []
    chunk_size_datapoints = int(chunk_size * rate)
    for (start, end), (key, _) in keys:
        print(start, end, key)
        result.append(key_transform(key).apply_to_song(
            data[start*chunk_size_datapoints:end*chunk_size_datapoints],
            rate,
            chunk_size,
            processes=8
        ))
    return np.concatenate(result)


def major_to_minor(minor_type):
    def _transform(key):
        if key.key_type == major:
            return minor_type(key.start)
        return Identity()
    return _transform

def minor_to_major(major_type):
    def _transform(key):
        if key.key_type == minor:
            return major_type(key.start)
        return Identity()
    return _transform
