from typing import Union, Iterator

ValueType = Union[int, str]
ValuesForParseType = Union[ValueType, list[ValueType], set[ValueType]]


class Enumeration:
    @classmethod
    def values_iter(cls) -> Iterator[ValueType]:
        big_dict = {}
        for class_ in reversed(cls.mro()):
            big_dict.update(class_.__dict__)
        big_dict.update(cls.__dict__)

        keys = list(big_dict.keys())

        for key in keys:
            if not isinstance(key, str):
                continue

            if key.startswith('__') or key.endswith('__'):
                continue

            value = big_dict[key]

            if type(value) not in [str, int]:
                continue

            yield value

    @classmethod
    def values_set(cls) -> set[ValueType]:
        return set(cls.values_iter())

    @classmethod
    def values_list(cls) -> list[ValueType]:
        return list(cls.values_iter())

    @classmethod
    def parse_values(cls, *values: ValuesForParseType, validate: bool = False) -> list[ValueType]:
        res = []

        for value in values:
            if isinstance(value, str) or isinstance(value, int):
                if validate is True and value not in cls.values_set():
                    raise ValueError(f"validate is True and {value} not in {cls.values_set()}")
                res.append(value)
            elif isinstance(value, list) or isinstance(values, set):
                for value_ in value:
                    if validate is True and value_ not in cls.values_set():
                        raise ValueError(f"validate is True and {value_} not in {cls.values_set()}")
                    res.append(value_)
            else:
                raise TypeError("bad type for value")

        return res

    @classmethod
    def parse_and_validate_values(cls, *values: ValuesForParseType) -> list[ValueType]:
        return cls.parse_values(*values, validate=True)