""" Concise UUID generation. """

import binascii
import math
import os
import uuid as _uu

SALT_STRINGS=[(1,'g'),(7,'o'),(9,'n')]

def insert_char(mystring, index, chartoinsert):
    if index > len(mystring):
        return mystring
    else:
        mystring   =  mystring[:index] + chartoinsert + mystring[index:]
        return mystring

def remove_char(mystring,index):
    if index > len(mystring):
        return mystring
    return mystring[:index] + mystring[index+1:]

def salt_string(string):
    """
      Add some 'random' letters in 'random' positions, to add extra layer of security

      Sort it ascending, so we do not alter the insert position for the unsalting
    """
    for tup in sorted(SALT_STRINGS, key=lambda x: x[0]):
        string = insert_char(string,tup[0],tup[1])
    return string

def unsalt_string(string):
    """
      Remove some 'random' letters in 'random' positions, so when decoding, obtain original value

      SALT_STRINGS is iterated descending order so we do not alter the length of the first
      portion of the string when we delete characters.

      Example:
          s = "abcdefghi", if we want to take positions 1 and 7, that will be
          characters 'b' and 'g', but if we take first 'b', then the 7th character
          will be 'h'. But if we take first the 7th, the first portion will remain untouched
          so still valid the relation between index and letter.
    """
    for tup in sorted(SALT_STRINGS, key=lambda x: x[0],reverse=True):
        string = remove_char(string,tup[0])
    return string

def int_to_string(number, alphabet, padding=None):
    """
    Convert a number to a string, using the given alphabet.
    The output has the most significant digit first.
    """
    output = ""
    alpha_len = len(alphabet)
    while number:
        number, digit = divmod(number, alpha_len)
        output += alphabet[digit]
    if padding:
        remainder = max(padding - len(output), 0)
        output = output + alphabet[0] * remainder
    return output[::-1]


def string_to_int(string, alphabet):
    """
    Convert a string to a number, using the given alphabet.
    The input is assumed to have the most significant digit first.
    """
    number = 0
    alpha_len = len(alphabet)
    for char in string:
        number = number * alpha_len + alphabet.index(char)
    return number


class ShortUUID(object):
    def __init__(self, alphabet=None):
        if alphabet is None:
            alphabet = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZ" "abcdefghijkmnopqrstuvwxyz")

        self.set_alphabet(alphabet)

    @property
    def _length(self):
        """
        Return the necessary length to fit the entire UUID given
        the current alphabet.
        """
        return int(math.ceil(math.log(2 ** 128, self._alpha_len)))

    def encode(self, uuid, pad_length=None):
        """
        Encode a UUID into a string (LSB first) according to the alphabet

        If leftmost (MSB) bits are 0, the string might be shorter.
        """
        if pad_length is None:
            pad_length = self._length
        #return int_to_string(uuid.int, self._alphabet, padding=pad_length)
        return salt_string(int_to_string(uuid.int, self._alphabet, padding=pad_length))

    def decode(self, string, legacy=False):
        """
        Decode a string according to the current alphabet into a UUID
        Raises ValueError when encountering illegal characters
        or a too-long string.

        If string too short, fills leftmost (MSB) bits with 0.

        Pass `legacy=True` if your UUID was encoded with a ShortUUID version
        prior to 0.6.0.
        """
        if legacy:
            string = string[::-1]
        string = unsalt_string(string)
        return _uu.UUID(int=string_to_int(string, self._alphabet))

    def uuid(self, name=None, pad_length=None):
        """
        Generate and return a UUID.

        If the name parameter is provided, set the namespace to the provided
        name and generate a UUID.
        """
        if pad_length is None:
            pad_length = self._length

        # If no name is given, generate a random UUID.
        if name is None:
            uuid = _uu.uuid4()
        elif name.lower().startswith(("http://", "https://")):
            uuid = _uu.uuid5(_uu.NAMESPACE_URL, name)
        else:
            uuid = _uu.uuid5(_uu.NAMESPACE_DNS, name)
        return self.encode(uuid, pad_length)

    def random(self, length=None):
        """
        Generate and return a cryptographically-secure short random string
        of the specified length.
        """
        if length is None:
            length = self._length

        random_num = int(binascii.b2a_hex(os.urandom(length)), 16)
        return int_to_string(random_num, self._alphabet, padding=length)[:length]

    def get_alphabet(self):
        """Return the current alphabet used for new UUIDs."""
        return "".join(self._alphabet)

    def set_alphabet(self, alphabet):
        """Set the alphabet to be used for new UUIDs."""

        # Turn the alphabet into a set and sort it to prevent duplicates
        # and ensure reproducibility.
        new_alphabet = list(sorted(set(alphabet)))
        if len(new_alphabet) > 1:
            self._alphabet = new_alphabet
            self._alpha_len = len(self._alphabet)
        else:
            raise ValueError("Alphabet with more than " "one unique symbols required.")

    def encoded_length(self, num_bytes=16):
        """
        Returns the string length of the shortened UUID.
        """
        factor = math.log(256) / math.log(self._alpha_len)
        return int(math.ceil(factor * num_bytes))


# For backwards compatibility
_global_instance = ShortUUID()
encode = _global_instance.encode
decode = _global_instance.decode
uuid = _global_instance.uuid
random = _global_instance.random
get_alphabet = _global_instance.get_alphabet
set_alphabet = _global_instance.set_alphabet

#s = ShortUUID()
#u = _uu.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}')
#print('U:{}'.format(u))
#print(s.encode(u))
#print(encode(u))
#>>> U:00010203-0405-0607-0809-0a0b0c0d0e0f
#>>> 2g24Hj8otnHKmged8ChbfJanE
#>>> 2g24Hj8otnHKmged8ChbfJanE

