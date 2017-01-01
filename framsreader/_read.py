def _deserialize(expression):
    if expression.strip() == 'null':
        return None
    if expression.strip() == '':
        # TODO msg
        raise ValueError('Empty value for "@Serialized" not allowed.')
    # TODO numbers
    # TODO strings
    # TODO lists
    # TODO dicts
    # TODO wutnot
    raise NotImplementedError()

    # String
    return exp


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
