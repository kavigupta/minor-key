
import unittest

from scipy.io import wavfile as wav

from key_identify import get_notes, to_string

class TestNoteToString(unittest.TestCase):
    def test_middle_c(self):
        self.assertEqual('C4', to_string(0))
    def test_middle_d_flat(self):
        self.assertEqual('Db4', to_string(1))
    def test_lower_c(self):
        self.assertEqual('C3', to_string(-12))

class TestNoteLookup(unittest.TestCase):
    def test_fmin(self):
        rate, value = wav.read('test_wavs/fmin.wav')
        notes = {to_string(note) for note in get_notes(rate, value, 6)}
        for note in 'F4', 'Ab4', 'C5':
            self.assertIn(note, notes)
    def test_cc(self):
        rate, value = wav.read('test_wavs/cc.wav')
        notes = {to_string(note) for note in get_notes(rate, value, 2)}
        for note in 'C4', 'C5':
            self.assertIn(note, notes)
    def test_cde(self):
        rate, value = wav.read('test_wavs/cde.wav')
        notes = {to_string(note) for note in get_notes(rate, value, 6)}
        for note in 'C4', 'D4', 'E4':
            self.assertIn(note, notes)

unittest.main()
