
import unittest

from scipy.io import wavfile as wav

from key_identify import get_notes, to_string, best_key_for_chords_incremental, best_multiple_keys_for_chords
from keys import Key, Keys, major, minor, ALL_MAJORS_MINORS

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

class TestBestKeyMatching(unittest.TestCase):
    def test_direct(self):
        result = list(best_key_for_chords_incremental([{0, 4}], ALL_MAJORS_MINORS))
        self.assertEqual([(Key(major, 0), 8)], result)
    def test_inversion(self):
        result = list(best_key_for_chords_incremental([{0, 5}], ALL_MAJORS_MINORS))
        self.assertEqual([(Key(major, 5), 8)], result)
    def test_progressive_info(self):
        result = list(best_key_for_chords_incremental([{0}, {5}], ALL_MAJORS_MINORS))
        self.assertEqual([(Key(major, 0), 5), (Key(major, 5), 8)], result)
    def test_progressive_minor(self):
        result = list(best_key_for_chords_incremental([{0}, {5}, {8}], ALL_MAJORS_MINORS))
        self.assertEqual([(Key(major, 0), 5), (Key(major, 5), 8), (Key(minor, 5), 11)], result)
    def test_no_change(self):
        result = list(best_key_for_chords_incremental([{0}, {5}, {9}], ALL_MAJORS_MINORS))
        self.assertEqual([(Key(major, 0), 5), (Key(major, 5), 8), (Key(major, 5), 11)], result)

class TestOverallKeyMatching(unittest.TestCase):
    def test_two_keys(self):
        result = best_multiple_keys_for_chords([{0}, {4}, {7}, {9}, {0}, {4}], 2, ALL_MAJORS_MINORS)
        self.assertEqual(Keys({(0, 3) : (Key(major, 0), 11), (3, 6) : (Key(minor, 9), 11)}), result)
    def test_two_overlapping_keys(self):
        result = best_multiple_keys_for_chords([{0}, {4}, {7}, {11}, {2}], 2, ALL_MAJORS_MINORS)
        self.assertEqual(Keys({(0, 2) : (Key(major, 0), 8), (2, 5) : (Key(major, 7), 11)}), result)

unittest.main()
