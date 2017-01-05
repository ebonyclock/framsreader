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
expdef_input_files = [f for f in os.listdir(input_files_root) if f.endswith(".expdef")]
# all_input_files = ["simple.gen"]
all_input_files = gen_input_files + expdef_input_files

parser_testcases = [
    ('1', 1),
    ('0', 0),
    ('a', 'a'),
    # TODO maybe tylda should be escaped?
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
    ('@Serialized:{"a":123,"b":[1,2,3] }', {"a": 123, "b": [1, 2, 3]}),
    ('@Serialized:XYZ[0,1,2]', (0,1,2)),
    ('@Serialized:Population<0x85f53a8>', 'Population<0x85f53a8>'),
    ('@Serialized:CrazyObject[{},{},[[]]]', 'CrazyObject[{},{},[[]]]')
]

parser_exception_testcases = [
    '@Serialized:   '
]

loads_testcases = [
    ('class:\nmlprop:~\nbla bla bla\n~\n', [{"_classname": "class", "mlprop": "bla bla bla\n"}]),
    ('class:\nmlprop:~\n\\~\n~\n', [{"_classname": "class", "mlprop": "~\n"}])
]
loads_exception_testcases = [
    'class:\nmlprop:~\n\\~\n~\nasdasd',
    'class:\nmlprop:~\n~\n~\n',
    'class:\nmlprop:~\n'
]


# TODO make more atomic tests, maybe
class ReferenceTest(unittest.TestCase):
    def test0(self):
        str_in = '@Serialized:[^0] '
        result = fr.default_parse(str_in)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 1)
        self.assertTrue(result is result[0])

    def test1(self):
        str_in = '@Serialized:[44,[^1]]'
        result = fr.default_parse(str_in)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 44)
        self.assertTrue(result[1] is result[1][0])

    def test2(self):
        str_in = '@Serialized:[[100],["abc"],[300,^2]]'
        result = fr.default_parse(str_in)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [100])
        self.assertEqual(result[1], ["abc"])
        self.assertEqual(result[2][0], 300)
        self.assertTrue(result[2][1] is result[1])

    def test3(self):
        str_in = '@Serialized:[[123,[]],["x",^0],^2]'
        result = fr.default_parse(str_in)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [123, []])
        self.assertTrue(isinstance(result[1], list))
        self.assertEqual(result[1][0], "x")
        self.assertTrue(result[2] is result[0][1])
        self.assertTrue(result[1][1] is result)

    def test4(self):
        str_in = '@Serialized:{"a":[33,44],"b":^1,"c":[33,44]}'
        result = fr.default_parse(str_in)
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(len(result), 3)
        self.assertListEqual(sorted(result.keys()), ["a", "b", "c"])

        self.assertEqual(result["a"], [33, 44])
        self.assertEqual(result["c"], [33, 44])

        self.assertFalse(result["c"] is result["a"])
        self.assertTrue(result["b"], result["a"])

    def test5(self):
        str_in = '@Serialized:[null, null, [1, 2], null, ^ 1]'
        result = fr.default_parse(str_in)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 5)
        self.assertListEqual(result[0:4], [None, None, [1, 2], None])
        self.assertTrue(result[2] is result[4])


class ParseValueTest(unittest.TestCase):
    @parameterized.expand(parser_testcases)
    def test_correct_parsing(self, input_val, output):
        self.assertEqual(output, fr.default_parse(input_val))

    @parameterized.expand(parser_exception_testcases)
    def test_parsing_exceptions(self, input_val):
        self.assertRaises(ValueError, fr.default_parse, input_val)


class LoadsTest(unittest.TestCase):
    @parameterized.expand(loads_testcases)
    def test_correct_loads(self, input_val, output):
        self.assertEqual(output, fr.loads(input_val))

    @parameterized.expand(loads_exception_testcases)
    def test_load_exceptions(self, input_val):
        self.assertRaises(ValueError, fr.loads, input_val)


class LoadTest(unittest.TestCase):
    @parameterized.expand(all_input_files)
    def test_correct_load(self, filename):
        file_path = os.path.join(input_files_root, filename)
        json_path = os.path.join(output_files_root, filename + ".json")
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
