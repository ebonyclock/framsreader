#!/usr/bin/env python3
import unittest
from nose_parameterized import parameterized
import os
import json

import framsreader as fr

test_files_root = "test_files"
input_files_root = os.path.join(test_files_root, "inputs")
output_files_root = os.path.join(test_files_root, "outputs")

gen_input_files = [f for f in os.listdir(input_files_root) if f.endswith(".gen")]
# gen_input_files = ["demo-chase.gen"]
all_input_files = gen_input_files

parser_testcases = [
    ('1', 1),
    ('0', 0),
    ('a', 'a'),
    ('generic string ~ with tylda', 'generic string ~ with tylda'),
    ('123', 123),
    ('0x123', 0x123),
    ('0X123', 0x123),
    ('+0X10', 16),
    ('-0x125', -0x125),
    ('-0xaa', -0xaa),
    ('0xaa', 0xaa),
    ('0xAA', 0xaa),
    ('-12.3', -12.3),
    ('12.3e+05', 12.3e+05),
    ('@Serialized:null', None),
    ('@Serialized: null', None),
    ('@Serialized:"@Serialized:"', '@Serialized:'),
    ('@Serialized:"\\""', '"'),
    ('@Serialized:"\\t"', '\t'),
    ('@Serialized:"\\n"', '\n'),
    ('@Serialized:1', 1),
    ('@Serialized:2.1', 2.1),
    ('@Serialized:+2.1', 2.1),
    ('@Serialized:-2.1', -2.1),
    ('@Serialized: +0X10  ', 16),
    ('@Serialized: 0X10  ', 16),
    ('@Serialized: 0XAA  ', 0xaa),
    ('@Serialized: 0Xaa  ', 0xaa),
    ('@Serialized:[]', []),
    ('@Serialized:[1,2,3]', [1, 2, 3]),
    ('@Serialized: [ +0X10 ] ', [16]),
    ('@Serialized:[ +0X10, null, "abc"] ', [16, None, "abc"]),
    ('@Serialized:[[[]]]', [[[]]]),
    ('@Serialized:{}', {}),
    ('@Serialized:{"a":123 }', {"a": 123}),
    ('@Serialized:{"a":123,"b":2 }', {"a": 123, "b": 2}),
    ('@Serialized:{"a":123,"b":[1,2,3] }', {"a": 123, "b": [1, 2, 3]})
]

parser_exception_testcases = [
    '@Serialized:   '
]

loads_testcases = [
    ('class:\nmlprop:~\nbla bla bla\n~\n', [{"class": "class", "mlprop": "bla bla bla\n"}]),
    ('class:\nmlprop:~\n\\~\n~\n', [{"class": "class", "mlprop": "~\n"}])
]
loads_exception_testcases = [
    'class:\nmlprop:~\n\\~\n~\nasdasd',
    'class:\nmlprop:~\n~\n~\n',
    'class:\nmlprop:~\n'
]


class TestParseValue(unittest.TestCase):
    @parameterized.expand(parser_testcases)
    def test_correct_parsing(self, input_val, output):
        self.assertEqual(output, fr.parse_property(input_val))

    @parameterized.expand(parser_exception_testcases)
    def test_parsing_exceptions(self, input_val):
        self.assertRaises(ValueError, fr.parse_property, input_val)


class TestLoads(unittest.TestCase):
    @parameterized.expand(loads_testcases)
    def test_correct_loads(self, input_val, output):
        self.assertEqual(output, fr.loads(input_val))

    @parameterized.expand(loads_exception_testcases)
    def test_load_exceptions(self, input_val):
        self.assertRaises(ValueError, fr.loads, input_val)


class TestLoad(unittest.TestCase):
    @parameterized.expand(all_input_files)
    def test_correct_load(self, filename):
        file_path = os.path.join(input_files_root, filename)
        json_path = os.path.join(output_files_root, filename.split(".")[0] + ".json")
        with self.subTest(i=file_path):
            result = fr.load(file_path)
            with open(json_path) as json_file:
                correct = json.load(json_file)
            self.assertEqual(len(result), len(correct))
            # self.assertListEqual(result, correct)
            for r, c in zip(result, correct):
                self.assertDictEqual(r, c)


if __name__ == '__main__':
    unittest.main()
