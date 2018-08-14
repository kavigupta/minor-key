"""
Contains model information regarding keys
"""

from collections import namedtuple

class KeyType(namedtuple('KeyType', ['name', 'note_value'])):
    """
    Represents a key type, generally either major or minor key.

    `note_value` is a dictionary mapping elements in range(12) to positive integer values
        representing how much the value should work
    """
    def score(self, note):
        """
        Get the score for the given note within this key, as if this key were C whatever.

        For example, minor.score(2) represents the score of D within minor
        """
        return self.note_value.get(note % 12, 0)
    def __repr__(self):
        return self.name

class Key(namedtuple('Key', ['key_type', 'start'])):
    """
    Represents a key, which is composed of a key type and starting key.
    """
    def score(self, note):
        """
        Gets the score for the given note within this key.

        For example, (A minor).score(2) gets the score of B within A minor
        """
        return self.key_type.score(note - self.start)
    def score_chord(self, chord):
        """
        Gets the score for the given set of notes within this key.

        TODO currently this just is the sum of the individual elements,
            but it can be more intelligent
        """
        return sum(self.score(note) for note in chord)
    def __repr__(self):
        return "Key(%s, %s)" % (self.key_type, self.start)

class Keys(namedtuple('Keys', ['range_to_key'])):
    """
    Represents a set of keys,
        each associated with a temporal range (start, end) a half-open interval
    """
    def additional(self, time_range, key, score):
        """
        Cosntructs a new Keys instance, but with the given time_range associated with the given key
        """
        result = dict(self.range_to_key.items())
        result[time_range] = (key, score)
        return Keys(result)
    @property
    def score(self):
        """
        Return the overall score
        """
        return sum(score for _, score in self.range_to_key.values())
    def __iter__(self):
        return iter(self.range_to_key.items())

major = KeyType("major", {0 : 5, 2 : 1, 4 : 3, 5 : 1, 7 : 3, 9 : 1, 11 : 1}) # pylint: disable=invalid-name
minor = KeyType("minor", {0 : 5, 2 : 1, 3 : 3, 5 : 1, 7 : 3, 8 : 1, 10 : 1, 11 : 1}) # pylint: disable=invalid-name
ALL_MAJORS_MINORS = [Key(typ, start) for typ in (major, minor) for start in range(12)]
