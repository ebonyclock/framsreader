import re as _re
import json


def _deserialize(expression):
    stripped_exp = expression.strip()
    if stripped_exp == '':
        # TODO msg
        raise ValueError('Empty value for "@Serialized" not allowed.')
    if stripped_exp == 'null':
        return None

    # String in quotes
    if _re.search('^".*"$', stripped_exp):
        string_exp = stripped_exp[1:-1]
        # TODO maybe support for more esscaped characters?
        # TODO maybe throw when " is not escaped?
        # TODO check if it really does what's si[[supposed to
        string_exp = _re.sub('\\\\t', '\t', string_exp)
        string_exp = _re.sub('\\\\"', '"', string_exp)
        string_exp = _re.sub('\\\\n', '\n', string_exp)
        return string_exp
    # Lists
    if _re.search('^\[.*\]$', stripped_exp):
        if stripped_exp[1:-1].strip() == "":
            return []
        list_exp = [_deserialize(x.strip()) for x in stripped_exp[1:-1].split(",")]
        return list_exp

    # Dicts:
    # TODO won't work for nested dicts and lists
    if _re.search('^{.*}$', stripped_exp):
        dictionary = dict()
        for pair in stripped_exp[1:-1].split(','):
            k, v = pair.split(":")
            dictionary[_deserialize(k)] = _deserialize(v)
        return dictionary
    # TODO dicts
    # TODO wutnot
    # raise NotImplementedError()

    # String
    return parse_value(expression)


def parse_value(value):
    if value.startswith("@Serialized:"):
        value = value.split(":", 1)[1]
        return _deserialize(value)

    stripped_value = value.strip()
    try:
        parsed_int = int(stripped_value, 0)
        return parsed_int
    except ValueError:
        pass
    try:
        parsed_float = float(stripped_value)
        return parsed_float

    except ValueError:
        pass

    return stripped_value


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
                            current_object[key] = parse_value(value)



            except RuntimeError as ex:
                # TODO better message?
                raise RuntimeError("Error parsing {}. Wrong syntax in line {}.".format(filename, line_num))
    return objects
