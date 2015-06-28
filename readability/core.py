import os


def required_from_env(key):
    """
    Retrieve a required variable from the current environment variables.

    Raises a ValueError if the env variable is not found or has no value.

    """
    val = os.environ.get(key)
    if not val:
        raise ValueError(
            "Required argument '{}' not supplied and not found in environment variables".format(key))
    return val
