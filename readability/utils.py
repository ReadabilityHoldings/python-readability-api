# -*- coding: utf-8 -*-

"""
readability.utils
~~~~~~~~~~~~~~~~~

This module provides various utils to the rest of the package.

"""

import logging

from datetime import datetime

from dateutil.parser import parse as parse_datetime


logger = logging.getLogger(__name__)


# map of filter names to a data type. This is used to map names to a
# casting function when needed.
filter_type_map = {
    'added_since': 'datetime',
    'added_until': 'datetime',
    'archive': 'int',
    'archived_since': 'datetime',
    'archived_until': 'datetime',
    'exclude_accessibility': 'string',
    'favorite': 'int',
    'favorited_since': 'datetime',
    'favorited_until': 'datetime',
    'domain': 'string',
    'only_delete': 'int',
    'opened_since': 'datetime',
    'opened_until': 'datetime',
    'order': 'string',
    'page': 'int',
    'per_page': 'int',
    'tags': 'string',
    'updated_since': 'datetime',
    'updated_until': 'datetime',
}


def cast_datetime_filter(value):
    """Cast a datetime filter value.

    :param value: string representation of a value that needs to be casted to
        a `datetime` object.

    """
    if isinstance(value, basestring):
        dtime = parse_datetime(value)

    elif isinstance(value, datetime):
        dtime = value
    else:
        raise ValueError('Received value of type {0}'.format(type(value)))

    return dtime.isoformat()


def cast_integer_filter(value):
    """Cast an integer filter value.

    Theses are usually booleans in Python but they need to be sent as
    1s and 0s to the API.

    :param value: boolean value that needs to be casted to an int
    """
    return int(value)


def filter_args_to_dict(filter_dict, accepted_filter_keys=[]):
    """Cast and validate filter args.

    :param filter_dict: Filter kwargs
    :param accepted_filter_keys: List of keys that are acceptable to use.

    """
    out_dict = {}
    for k, v in filter_dict.items():
        # make sure that the filter k is acceptable
        # and that there is a value associated with the key
        if k not in accepted_filter_keys or v is None:
            logger.debug(
                'Filter was not in accepted_filter_keys or value is None.')
            # skip it
            continue
        filter_type = filter_type_map.get(k, None)

        if filter_type is None:
            logger.debug('Filter key not foud in map.')
            # hmm, this was an acceptable filter type but not in the map...
            # Going to skip it.
            continue

        # map of casting funcitons to filter types
        filter_cast_map = {
            'int': cast_integer_filter,
            'datetime': cast_datetime_filter
        }
        cast_function = filter_cast_map.get(filter_type, None)

        # if we get a cast function, call it with v. If not, just use v.
        if cast_function:
            out_value = cast_function(v)
        else:
            out_value = v
        out_dict[k] = out_value

    return out_dict
