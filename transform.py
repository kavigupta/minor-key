"""
Module containing methods for transforming notes
"""

from abc import ABCMeta, abstractmethod
from functools import partial
import multiprocessing as multi

import numpy as np

from fftutils import convert_to_note, convert_to_index


class Transform(metaclass=ABCMeta):
    """
    Represents an operation on notes
    """
    @abstractmethod
    def transform(self, note):
        """
        Takes in the given note (in 12ths of an octave above middle C) and outputs a modified note
        """
    def transform_microtone(self, note):
        """
        Transforms a floating note, for example 0.5 is a quarter tone above middle C.

        By default, this process involves treating any deviation from the nearest
            integer as tuning, and simply passes it through
        """
        rounded_note = int(np.round(note))
        return self.transform(rounded_note) - rounded_note + note
    def apply_to_sample(self, sample, rate):
        """
        Apply this transformation to a given sample
        """
        freqs = np.fft.fft(sample)
        result = np.zeros_like(freqs)
        for idx in range(freqs.size // 2 + 1):
            note = convert_to_note(freqs, rate, idx)
            modified_note = self.transform_microtone(note)
            modified_idx = convert_to_index(freqs, rate, modified_note)
            result[modified_idx] += freqs[idx]
            if modified_idx != 0 and 2 * modified_idx < freqs.size:
                result[-modified_idx] += np.conj(freqs[idx])
        return np.round(np.real(np.fft.ifft(result))).astype(np.int16)
    def apply_to_song(self, data, rate, sample_length, processes=1):
        """
        Apply this transformation to a song by samples,
            where each sample is `sample_length` seconds long
        """

        sample_length_datapoints = int(rate * sample_length)

        samples = [data[start_idx:start_idx + sample_length_datapoints]
                   for start_idx in range(0, len(data), sample_length_datapoints)]

        by_sample = multi.Pool(processes=processes).map(
            partial(self.apply_to_sample, rate=rate),
            samples
        )
        return np.concatenate(by_sample)

class Identity(Transform):
    """
    Does nothing. Overrides even non-abstract methods for efficiency purposes
    """
    def transform(self, note):
        return note
    def transform_microtone(self, note):
        return note
    def apply_to_sample(self, sample, rate):
        return sample
    def apply_to_song(self, data, rate, sample_length, processes=1):
        return data

class ToMinorTransform(Transform, metaclass=ABCMeta):
    """
    Represents a transform to a minor key
    """
    def __init__(self, key_note):
        self.key_note = key_note
    def transform(self, note):
        return note - self.is_depressed(note)
    def is_depressed(self, note):
        """
        Returns whether or not the given note should be depressed
        """
        return (note - self.key_note) % 12 in self.notes_to_be_depressed()
    @abstractmethod
    def notes_to_be_depressed(self):
        """
        Return a set of notes that are to be depressed by a half tone to get the minor version.
        """

class MajorToHarmonicMinor(ToMinorTransform):
    """
    Transforms to a harmonic minor: C, D, Eb, F, G, Ab, B
    """
    def notes_to_be_depressed(self):
        return {4, 9}

class MajorToNaturalMinor(ToMinorTransform):
    """
    Transforms to a natural minor: C, D, Eb, F, G, Ab, Bb
    """
    def notes_to_be_depressed(self):
        return {4, 9, 11}
