#!/usr/bin/env python3
import unittest
from nose_parameterized import parameterized
import os
import json

import framsreader as fr

test_files_root = "test_files"
input_files_root = os.path.join(test_files_root, "inputs")
output_files_root = os.path.join(test_files_root, "outputs")

# gen_input_files = [f for f in os.listdir(input_files_root) if f.endswith(".gen")]
gen_input_files = ["simple.gen"]
all_input_files = gen_input_files

parser_testcases = [
    ('1', 1),
    ('0', 0),
    ('a', 'a'),
    ('generic string ~ with tylda', 'generic string ~ with tylda'),
    ('123', 123),
    ('0x123', 291),
    ('-0x125', -0x125),
    ('-12.3', -12.3),
    ('12.3e+05', 12.3e+05),
    ('@Serialized:null', None),
    ('@Serialized: null', None),
    ('@Serialized:"@Serialized:"', '@Serialized:'),

]

parser_exception_testcases = [
    '@Serialized:   '
]


class TestParseValue(unittest.TestCase):
    @parameterized.expand(parser_testcases)
    def test_correct_parsing(self, input_val, output):
        self.assertEqual(output, fr.parse_value(input_val))

    @parameterized.expand(parser_exception_testcases)
    def test_parsing_exceptions(self, input_val):
        self.assertRaises(ValueError, fr.parse_value, input_val)


class TestFramsRead(unittest.TestCase):
    @parameterized.expand(all_input_files)
    def test_parse_from_file(self, filename):
        file_path = os.path.join(input_files_root, filename)
        json_path = os.path.join(output_files_root, filename.split(".")[0] + ".json")
        with self.subTest(i=file_path):
            result = sorted(fr.read(file_path))
            with open(json_path) as json_file:
                correct = sorted(json.load(json_file))
            self.assertEqual(len(result), len(correct))
            # self.assertListEqual(result, correct)
            for r, c in zip(result, correct):
                self.assertDictEqual(r, c)


if __name__ == '__main__':
    unittest.main()
