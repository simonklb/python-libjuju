#
# Module that parses constraints
#
# The current version of juju core expects the client to take
# constraints given in the form "mem=10G foo=bar" and parse them into
# json that looks like {"mem": 10240, "foo": "bar"}. This module helps us
# accomplish that task.
#
# We do not attempt to duplicate the checking done in
# client/_client.py:Value here. That class will verify that the
# constraints keys are valid, and that we can successfully dump the
# constraints dict to json.
#
# Once https://bugs.launchpad.net/juju/+bug/1645402 is addressed, this
# module should be deprecated.
#

import re

# Matches on a string specifying memory size
MEM = re.compile('^[1-9][0-9]*[MGTP]$')

# Multiplication factors to get Megabytes
FACTORS = {
    "M": 1,
    "G": 1024,
    "T": 1024 * 1024,
    "P": 1024 * 1024 * 1024
}

def parse(constraints):
    """
    Constraints must be expressed as a string containing only spaces
    and key value pairs joined by an '='.

    """
    if constraints is None:
        return None

    if type(constraints) is dict:
        # Fowards compatibilty: already parsed
        return constraints

    constraints = {
        normalize_key(k): normalize_value(v) for k, v in [
            s.split("=") for s in constraints.split(" ")]}

    return constraints


def normalize_key(key):
    key = key.strip()

    key = key.replace("-", "_")  # Our _client lib wants "_" in place of "-"
    return key


def normalize_value(value):
    value = value.strip()

    if MEM.match(value):
        # Translate aliases to Megabytes. e.g. 1G = 10240
        return int(value[:-1]) * FACTORS[value[-1:]]

    if "," in value:
        # Handle csv strings.
        values = value.split(",")
        values = [normalize_value(v) for v in values]
        return values

    return value
