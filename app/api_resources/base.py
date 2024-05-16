import uuid

from flask_restx import fields


def json_list(value):
    if type(value) != list:
        print(value)
        raise ValueError('expected a list!')
    return value


class UidFields(fields.Raw):
    __schema_type__ = "string"

    def format(self, value):
        if isinstance(value, uuid.UUID):
            return value.hex
        elif isinstance(value, str):
            return value
        else:
            return value


class CountFields(fields.Raw):
    def format(self, value):
        return len(value)


from flask_restx.inputs import datetime_from_iso8601
from datetime import datetime, time


def time_from_iso8601(value):
    """
    Turns an ISO8601 formatted date into a date object.

    Example::

        inputs.date_from_iso8601("2012-01-01")



    :param str value: The ISO8601-complying string to transform
    :return: A time
    :rtype: time
    :raises ValueError: if value is an invalid date literal

    """
    return datetime_from_iso8601(value).time()


# time_from_iso8601.__schema__ = {"type": "string", "format": "time"}


class Time(fields.Date):
    """
    Return a formatted date string in UTC in ISO 8601.

    See :meth:`datetime.date.isoformat` for more info on the ISO 8601 format.
    """

    __schema_format__ = "time"

    def __init__(self, **kwargs):
        kwargs.pop("dt_format", None)
        super(Time, self).__init__(dt_format="iso8601", **kwargs)

    def parse(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            return time_from_iso8601(value)
        elif isinstance(value, datetime):
            return value.time()
        elif isinstance(value, time):
            return value
        else:
            raise ValueError("Unsupported Date format")
