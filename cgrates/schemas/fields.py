from rfc3339 import rfc3339

from datetime import time
from schematics.types import (
    StringType as DefaultStringType, DateTimeType as DefaultDateTimeType,
    FloatType, IntType, ListType, BooleanType, BaseType, DictType
)



class ISODateTimeType(DefaultDateTimeType):
    SERIALIZED_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class RFC3339DateTimeType(DefaultDateTimeType):
    SERIALIZED_FORMAT = lambda kls, value: rfc3339(value)


class SecondsType(IntType):

    def convert(self, value, context=None):
        if isinstance(value, int):
            return value

        value = int(value.replace("s", "")) if value else None

        if not value:
            return None

        return self.to_native(value, context)

    def to_primitive(self, value, context=None):
        value = super(SecondsType, self).to_primitive(value, context=context)
        return "{}s".format(value)


class StringType(DefaultStringType):
    def convert(self, value, context=None):
        if not value:
            return None

        return self.to_native(value, context)


class TimeType(StringType):

    def convert(self, value, context=None):
        return value

    def to_primitive(self, value, context=None):
        if not value:
            return None

        if isinstance(value, time):
            return value.strftime("%H:%M:%S")

        return value

class AnyOrListType(ListType):

    def convert(self, value, context=None):
        if value == "*any":
            return []

        if isinstance(value, list):
            return value

        return value.split(";")


    def export(self, value, format, context=None):
        result = super(AnyOrListType, self).export(value, format=format, context=context)
        return ";".join([str(x) for x in result]) if result else "*any"

