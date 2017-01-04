import re as _re

INT_FLOAT_REGEX = r'([+|-]?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?'
HEX_NUMBER_REGEX = r'[+|-]?0[xX][\da-fA-F]*'
NUMBER_REGEX = '({}|{})'.format(HEX_NUMBER_REGEX, INT_FLOAT_REGEX)
TYLDA_REGEX = '(?<![\\\\])(~)'
QUOTE_REGEX = '(?<![\\\\])(")'
ESCAPED_QUOTE_REGEX = '\\\\"'
ESCAPED_TAB_REGEX = '\\\\t'
ESCAPED_NEWLINE_REGEX = '\\\\n'
ESCAPED_TYLDA_REGEX = '\\\\~'

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


def _parse_simple_value(value):
    assert isinstance(value, str)
    try:
        parsed_number = _str_to_number(value)
        return parsed_number
    except ValueError:
        pass

    return value.strip()


def parse_property(str_property):
    assert isinstance(str_property, str)
    if str_property.startswith("@Serialized:"):
        prop = str_property.split(":", 1)[1]
        prop = _deserialize(prop)
        return prop
    else:
        return _parse_simple_value(str_property)


def _deserialize(expression):
    stripped_exp = expression.strip()
    if stripped_exp == '':
        # TODO msg
        raise ValueError('Empty value for "@Serialized" not allowed.')
    # Just load with json ...

    if stripped_exp == 'null':
        return None

    objects = []
    main_object_determined = False
    main_object = None
    expect_dict_value = False
    last_dict_key = None
    exp = stripped_exp

    while len(exp) > 0:
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
        if exp[0] == ",":
            if not (isinstance(objects[-1], list) or (isinstance(objects[-1], dict) and not expect_dict_value)):
                # TODO msg
                raise ValueError()
            else:
                exp = exp[1:].strip()
        # List start
        if exp[0] == "[":
            current_object = list()
            exp = exp[1:]
        elif exp[0] == "{":
            current_object = dict()
            exp = exp[1:]
        elif exp[0] == "]":
            if not isinstance(objects[-1], list):
                # TODO msg
                raise ValueError()
            else:
                objects.pop()
                exp = exp[1:].strip()
                continue

        elif exp[0] == "}":
            if not isinstance(objects[-1], dict):
                # TODO msg
                raise ValueError()
            else:
                objects.pop()
                exp = exp[1:].strip()
                continue
        # String
        elif exp[0] == '"':
            exp = exp[1:]
            str_end_match = _re.search(QUOTE_REGEX, exp)
            if str_end_match is None:
                # TODO message
                raise ValueError()
            str_end = str_end_match.span()[0]
            s = exp[:str_end]
            exp = exp[str_end+1:]
            s = _re.sub(ESCAPED_QUOTE_REGEX, '"', s)
            s = _re.sub(ESCAPED_TAB_REGEX, '\t', s)
            s = _re.sub(ESCAPED_NEWLINE_REGEX, '\n', s)
            current_object = s

        elif exp.startswith("null"):
            current_object = None
            exp = exp[4:]
        # NUMBER
        # Maybe check if alfanumeric or sumthing?
        elif _re.match(NUMBER_REGEX, exp) is not None:
            match = _re.match(NUMBER_REGEX, exp)
            number_as_str = match.group()
            exp = exp[match.span()[1]:]
            current_object = _str_to_number(number_as_str)

        else:
            # TODO some other object types?
            raise ValueError()

        if len(objects) > 0:
            if isinstance(objects[-1], list):
                objects[-1].append(current_object)
            elif isinstance(objects[-1], dict):
                if expect_dict_value:
                    objects[-1][last_dict_key] = current_object
                    last_dict_key = None
                    expect_dict_value = False
                else:
                    last_dict_key = current_object
                    expect_dict_value = True
        # TODO support for other types of objects?
        if isinstance(current_object, (list, dict)):
            objects.append(current_object)

        if not main_object_determined:
            main_object_determined = True
            main_object = current_object
        exp = exp.strip()

    # raise NotImplementedError()

    # String
    return main_object


def loads(s, *args, **kwargs):
    assert isinstance(s, str)
    lines = s.split("\n")
    multiline_value = None
    multiline_key = None
    current_object = None
    objects = []
    parsing_error = False
    for line_num, line in enumerate(lines):
        try:
            if multiline_key is not None:
                endmatch = _re.search(TYLDA_REGEX, line)
                # print(line)
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
                # TODO this regex catches newline somhow
                value = _re.sub(ESCAPED_TYLDA_REGEX, '~', value)
                multiline_value += value
                if endmatch is not None:
                    current_object[multiline_key] = multiline_value
                    multiline_value = None
                    multiline_key = None
            # TODO raise error when trailing ~ is not found
            # Ignores the comment line
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
                        # TODO maybe throw when multiple colons?
                        # if suffix !="":
                        #     raise RuntimeError()
                        current_object = {"class": class_name}
                        objects.append(current_object)
                        continue

                if current_object is not None:
                    key, value = line.split(":", 1)
                    if value.strip() == "~":
                        multiline_value = ""
                        multiline_key = key
                    else:
                        current_object[key] = parse_property(value)

        except ValueError:
            raise ValueError()
            parsing_error = True
            break
    if multiline_key is not None:
        # TODO msg
        raise ValueError()
    if parsing_error:
        # TODO better message?
        raise ValueError("Parsing error. Incorrect syntax in line {}:\n{}".format(line_num, line))

    return objects


def laod(filename, *args, **kwargs):
    file = open(filename)
    s = file.read()
    file.close()
    return loads(s, *args, **kwargs)
