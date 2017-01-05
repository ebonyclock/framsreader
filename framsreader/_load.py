import re as _re
from collections import defaultdict

INT_FLOAT_REGEX = r'([+|-]?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?'
NATURAL_REGEX = r'(?:0|[1-9]\d*)'
HEX_NUMBER_REGEX = r'[+|-]?0[xX][\da-fA-F]*'
NUMBER_REGEX = '({}|{})'.format(HEX_NUMBER_REGEX, INT_FLOAT_REGEX)
TYLDA_REGEX = '(?<![\\\\])(~)'
QUOTE_REGEX = '(?<![\\\\])(")'
ESCAPED_QUOTE_REGEX = '\\\\"'
ESCAPED_TAB_REGEX = '\\\\t'
ESCAPED_NEWLINE_REGEX = '\\\\n'
ESCAPED_TYLDA_REGEX = '\\\\~'


def _parse_simple_value(value):
    assert isinstance(value, str)
    try:
        parsed_number = _str_to_number(value)
        return parsed_number
    except ValueError:
        pass

    return value.strip()


def _str_to_number(s):
    assert isinstance(s, str)
    s = s.strip()

    try:
        parsed_int = int(s, 0)
        return parsed_int
    except ValueError:
        pass
    try:
        parsed_float = float(s)
        return parsed_float

    except ValueError:
        pass
    # TODO msg
    raise ValueError()


def default_parse(value, *args, **kwargs):
    assert isinstance(value, str)
    if value.startswith("@Serialized:"):
        prop = value.split(":", 1)[1]
        prop = deserialize(prop)
        return prop
    else:
        return _parse_simple_value(value)


def parse_property(value, key):
    raise NotImplementedError()


def extract_string(exp):
    exp = exp[1:]
    str_end_match = _re.search(QUOTE_REGEX, exp)
    if str_end_match is None:
        # TODO msg
        raise ValueError()
    str_end = str_end_match.span()[0]
    s = exp[:str_end]
    reminder = exp[str_end + 1:]
    s = _re.sub(ESCAPED_QUOTE_REGEX, '"', s)
    s = _re.sub(ESCAPED_TAB_REGEX, '\t', s)
    s = _re.sub(ESCAPED_NEWLINE_REGEX, '\n', s)
    return s, reminder


def extract_number(exp):
    match = _re.match(NUMBER_REGEX, exp)
    number_as_str = match.group()
    reminder = exp[match.span()[1]:]
    number = _str_to_number(number_as_str)
    return number, reminder


# TODO maybe do it nicer??
def extract_xyz(exp):
    exp = exp.strip()
    if not exp.startswith('XYZ['):
        # TODO msg
        raise ValueError()
    exp = exp[4:]
    x , exp = extract_number(exp)
    x = float(x)
    exp = exp.strip()
    if exp[0] != ',':
        # TODO msg
        raise ValueError()
    exp = exp[1:]
    y, exp = extract_number(exp)
    y = float(y)
    exp = exp.strip()
    if exp[0] != ',':
        # TODO msg
        raise ValueError()
    exp = exp[1:]
    z, exp = extract_number(exp)
    z = float(z)
    exp = exp.strip()
    if exp[0] != ']':
        # TODO msg
        raise ValueError()
    return (x,y,z), exp[1:]


def extract_reference(exp):
    exp = exp[1:].strip()
    i_match = _re.match(NATURAL_REGEX, exp)
    if i_match is None:
        # TODO msg
        raise ValueError()
    else:
        end_i = i_match.span()[1]
        ref_index = int(exp[:end_i])
        reminder = exp[end_i:]
    return ref_index, reminder


def extract_custom_object(exp):
    raise NotImplementedError()


def deserialize(expression):
    stripped_exp = expression.strip()
    if stripped_exp == '':
        # TODO msg
        raise ValueError('Empty value for "@Serialized" not allowed.')
    # Just load with json ...

    if stripped_exp == 'null':
        return None

    objects = []
    references = []
    current_object_is_custom = False
    main_object_determined = False
    main_object = None
    expect_dict_value = False
    last_dict_key = None
    exp = stripped_exp
    opened_lists = 0
    opened_dicts = 0

    while len(exp) > 0:
        current_object_is_reference = False
        if main_object_determined and len(objects) == 0:
            # TODO msg
            raise ValueError()
        if expect_dict_value:
            if exp[0] == ':':
                exp = exp[1:].strip()
            else:
                # TODO msg
                raise ValueError()
        # List continuation
        # TODO support for XYZ tuples
        if exp[0] == ",":
            if not (isinstance(objects[-1], list) or (isinstance(objects[-1], dict) and not expect_dict_value)):
                # TODO msg
                raise ValueError()
            else:
                exp = exp[1:].strip()

        if exp[0] == "]":
            if not isinstance(objects[-1], list):
                # TODO msg
                raise ValueError()
            else:
                opened_lists -= 1
                objects.pop()
                exp = exp[1:].strip()
                continue
        elif exp[0] == "}":
            opened_dicts -= 1
            if not isinstance(objects[-1], dict):
                # TODO msg
                raise ValueError()
            else:
                objects.pop()
                exp = exp[1:].strip()
                continue
        # List start
        elif exp.startswith("null"):
            current_object = None
            exp = exp[4:]
        elif exp.startswith("XYZ"):
            current_object, exp = extract_xyz(exp)
        elif exp[0] == "[":
            current_object = list()
            opened_lists += 1
            exp = exp[1:]
        elif exp[0] == "{":
            current_object = dict()
            opened_dicts += 1
            exp = exp[1:]
        elif exp[0] == '"':
            current_object, exp = extract_string(exp)
        elif _re.match(NUMBER_REGEX, exp) is not None:
            current_object, exp = extract_number(exp)
        # TODO move to separate function
        elif exp[0] == '^':
            i, exp = extract_reference(exp)
            if i >= len(references):
                # TODO msg
                raise ValueError()
            current_object = references[i]
            current_object_is_reference = True
        else:
            current_object, reminder = extract_custom_object(exp)

        if len(objects) > 0:
            if isinstance(objects[-1], list):
                objects[-1].append(current_object)
            elif isinstance(objects[-1], dict):
                if expect_dict_value:
                    objects[-1][last_dict_key] = current_object
                    last_dict_key = None
                    expect_dict_value = False
                else:
                    if not isinstance(current_object, str):
                        # TODO msg
                        raise ValueError()
                    last_dict_key = current_object
                    expect_dict_value = True
        # TODO support for other types of objects?
        if isinstance(current_object, (list, dict, tuple)) and not current_object_is_reference:
            objects.append(current_object)
            references.append(current_object)
        if not main_object_determined:
            main_object_determined = True
            main_object = current_object
        exp = exp.strip()

    if opened_lists != 0:
        # TODO msg
        raise ValueError()
    if opened_dicts != 0:
        # TODO msg
        raise ValueError()
    return main_object


def loads(s, *args, **kwargs):
    assert isinstance(s, str)
    lines = s.split("\n")
    multiline_value = None
    multiline_key = None
    current_object = None
    objects = []
    parsing_error = False
    parse_functions = defaultdict(lambda: default_parse)
    parse_fun = None
    for line_num, line in enumerate(lines):
        try:
            if multiline_key is not None:
                endmatch = _re.search(TYLDA_REGEX, line)
                if endmatch is not None:
                    endi = endmatch.span()[0]
                    value = line[0:endi]
                    reminder = line[endi + 1:].strip()
                    if reminder != "":
                        # TODO msg
                        raise ValueError()
                else:
                    value = line + "\n"

                if _re.search(TYLDA_REGEX, value) is not None:
                    # TODO msg
                    raise ValueError()
                value = _re.sub(ESCAPED_TYLDA_REGEX, '~', value)
                multiline_value += value
                if endmatch is not None:
                    current_object[multiline_key] = multiline_value
                    multiline_value = None
                    multiline_key = None

            # Ignores comment lines (if outside multiline prop)
            elif line.startswith("#"):
                continue
            else:
                line = line.strip()
                if current_object is not None:
                    if line == "":
                        current_object = None
                        continue
                else:
                    if ":" in line:
                        class_name, suffix = line.split(":", 1)
                        # TODO maybe raise error when something's after classname
                        # if suffix !="":
                        #     raise ValueError()
                        current_object = {"_classname": class_name}
                        parse_fun = parse_functions[class_name]
                        objects.append(current_object)
                        continue

                if current_object is not None:
                    key, value = line.split(":", 1)
                    # TODO check if the key is supported for given class
                    if key.strip() == "":
                        # TODO msg
                        raise ValueError()
                    if value.strip() == "~":
                        multiline_value = ""
                        multiline_key = key
                    else:
                        value = parse_fun(value, key)
                        current_object[key] = value

        except ValueError:
            raise ValueError()
            parsing_error = True
            break
    if multiline_key is not None:
        # TODO msg
        raise ValueError()
    if parsing_error:
        raise ValueError("Parsing error. Incorrect syntax in line {}:\n{}".format(line_num, line))

    return objects


def load(filename, *args, **kwargs):
    file = open(filename)
    s = file.read()
    file.close()
    return loads(s, *args, **kwargs)
