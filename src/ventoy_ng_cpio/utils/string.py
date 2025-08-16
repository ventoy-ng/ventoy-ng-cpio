def assert_stringifyable_value(v: object) -> bool:
    if v.__str__ != object.__str__:
        return True
    raise ValueError("Not stringifyable value: {}".format(
        v.__class__.__name__
    ))
