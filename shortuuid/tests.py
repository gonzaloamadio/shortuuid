import os
import string
import sys
import unittest
from collections import defaultdict
from uuid import UUID, uuid4

from shortuuid.main import ShortUUID, decode, encode, get_alphabet, random, set_alphabet, uuid

sys.path.insert(0, os.path.abspath(__file__ + "/../.."))


class LegacyShortUUIDTest(unittest.TestCase):
    def test_generation(self):
        self.assertTrue(20 < len(uuid()) < 24)
        self.assertTrue(20 < len(uuid("http://www.example.com/")) < 24)
        self.assertTrue(20 < len(uuid("HTTP://www.example.com/")) < 24)
        self.assertTrue(20 < len(uuid("example.com/")) < 24)

    def test_encoding(self):
        ui = UUID("{3b1f8b40-222c-4a6e-b77e-779d5a94e21c}")
        self.assertEqual(encode(ui), "bYRT25J5s7Bniqr4b58cXC")

    def test_decoding(self):
        ui = UUID("{3b1f8b40-222c-4a6e-b77e-779d5a94e21c}")
        self.assertEqual(decode("bYRT25J5s7Bniqr4b58cXC"), ui)

    def test_alphabet(self):
        backup_alphabet = get_alphabet()

        alphabet = "01"
        set_alphabet(alphabet)
        self.assertEqual(alphabet, get_alphabet())

        set_alphabet("01010101010101")
        self.assertEqual(alphabet, get_alphabet())

        self.assertEqual(set(uuid()), set("01"))
        self.assertTrue(116 < len(uuid()) < 140)

        ui = uuid4()
        self.assertEqual(ui, decode(encode(ui)))

        ui = uuid()
        self.assertEqual(ui, encode(decode(ui)))

        self.assertRaises(ValueError, set_alphabet, "1")
        self.assertRaises(ValueError, set_alphabet, "1111111")

        set_alphabet(backup_alphabet)

        self.assertRaises(ValueError, lambda x: ShortUUID(x), "0")

    def test_random(self):
        self.assertEqual(len(random()), 22)
        for i in range(1, 100):
            self.assertEqual(len(random(i)), i)


class ClassShortUUIDTest(unittest.TestCase):
    def test_generation(self):
        su = ShortUUID()
        self.assertTrue(20 < len(su.uuid()) < 24)
        self.assertTrue(20 < len(su.uuid("http://www.example.com/")) < 24)
        self.assertTrue(20 < len(su.uuid("HTTP://www.example.com/")) < 24)
        self.assertTrue(20 < len(su.uuid("example.com/")) < 24)

    def test_encoding(self):
        su = ShortUUID()
        ui = UUID("{3b1f8b40-222c-4a6e-b77e-779d5a94e21c}")
        self.assertEqual(su.encode(ui), "bYRT25J5s7Bniqr4b58cXC")

        ui = UUID("{00010203-0405-0607-0809-0a0b0c0d0e0f}")
        self.assertEqual(su.encode(ui), "2g24Hj8otnHKmged8ChbfJanE")




    def test_decoding(self):
        su = ShortUUID()
        ui = UUID("{3b1f8b40-222c-4a6e-b77e-779d5a94e21c}")
        self.assertEqual(su.decode("bYRT25J5s7Bniqr4b58cXC"), ui)

    def test_random(self):
        su = ShortUUID()
        for i in range(1000):
            self.assertEqual(len(su.random()), 22)

        for i in range(1, 100):
            self.assertEqual(len(su.random(i)), i)

    def test_alphabet(self):
        alphabet = "01"
        su1 = ShortUUID(alphabet)
        su2 = ShortUUID()

        self.assertEqual(alphabet, su1.get_alphabet())

        su1.set_alphabet("01010101010101")
        self.assertEqual(alphabet, su1.get_alphabet())

        self.assertEqual(set(su1.uuid()), set("01"))
        self.assertTrue(116 < len(su1.uuid()) < 140)
        self.assertTrue(20 < len(su2.uuid()) < 24)

        ui = uuid4()
        self.assertEqual(ui, su1.decode(su1.encode(ui)))

        ui = su1.uuid()
        self.assertEqual(ui, su1.encode(su1.decode(ui)))

        self.assertRaises(ValueError, su1.set_alphabet, "1")
        self.assertRaises(ValueError, su1.set_alphabet, "1111111")

    def test_encoded_length(self):
        su1 = ShortUUID()
        self.assertEqual(su1.encoded_length(), 22)

        base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"

        su2 = ShortUUID(base64_alphabet)
        self.assertEqual(su2.encoded_length(), 22)

        binary_alphabet = "01"
        su3 = ShortUUID(binary_alphabet)
        self.assertEqual(su3.encoded_length(), 128)

        su4 = ShortUUID()
        self.assertEqual(su4.encoded_length(num_bytes=8), 11)


class ShortUUIDPaddingTest(unittest.TestCase):
    def test_padding(self):
        su = ShortUUID()
        random_uid = uuid4()
        smallest_uid = UUID(int=0)

        encoded_random = su.encode(random_uid)
        encoded_small = su.encode(smallest_uid)

        self.assertEqual(len(encoded_random), len(encoded_small))

    def test_decoding(self):
        su = ShortUUID()
        random_uid = uuid4()
        smallest_uid = UUID(int=0)

        encoded_random = su.encode(random_uid)
        encoded_small = su.encode(smallest_uid)

        self.assertEqual(su.decode(encoded_small), smallest_uid)
        self.assertEqual(su.decode(encoded_random), random_uid)

    def test_consistency(self):
        su = ShortUUID()
        num_iterations = 1000
        uid_lengths = defaultdict(int)

        for count in range(num_iterations):
            random_uid = uuid4()
            encoded_random = su.encode(random_uid)
            uid_lengths[len(encoded_random)] += 1
            decoded_random = su.decode(encoded_random)

            self.assertEqual(random_uid, decoded_random)

        self.assertEqual(len(uid_lengths), 1)
        uid_length = next(iter(uid_lengths.keys()))  # Get the 1 value

        self.assertEqual(uid_lengths[uid_length], num_iterations)


if __name__ == "__main__":
    unittest.main()
