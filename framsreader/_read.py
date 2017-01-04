import re as _re
import json

INT_FLOAT_REGEX = r'([+|-]?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?'
HEX_NUMBER_REGEX = r'[+|-]?0[xX][\da-fA-F]*'
NUMBER_REGEX = '({}|{})'.format(HEX_NUMBER_REGEX, INT_FLOAT_REGEX)


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
    current_object = None
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
            str_end_match = _re.search('[^\\\\](")', exp)
            if str_end_match is None:
                # TODO message
                raise ValueError()
            str_end = str_end_match.span()[1] - 1
            s = exp[1:str_end]
            exp = exp[str_end + 1:]
            s = _re.sub('\\\\"', '"', s)
            s = _re.sub('\\\\t', '\t', s)
            s = _re.sub('\\\\n', '\n', s)
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


def read(filename, *args, **kwargs):
    objects = []
    with open(filename) as file:
        multiline_value = None
        current_object = None

        for line_num, line in enumerate(file):
            try:
                if multiline_value:
                    # TODO append
                    # TODO check if \~ is there
                    # TODO check if ~ is there
                    raise NotImplementedError()
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
                    # Ignores the comment line


                    if current_object is not None:
                        key, value = line.split(":", 1)

                        if multiline_value and "~" in value and not "\~" in value:
                            multiline_value = ""
                            # TODO should this be checked also when not in multiline value?
                            # TODO start multiline prop
                            raise NotImplementedError()
                        else:
                            current_object[key] = parse_property(value)

            except RuntimeError:
                # TODO better message?
                raise RuntimeError("Error parsing {}. Wrong syntax in line {}.".format(filename, line_num))
    return objects
