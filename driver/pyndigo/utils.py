"""
Some utility functions.

"""
from datetime import datetime, timezone
import sys

def get_timestamp() -> str:
    """
    Gets the current timestamp in the format that INDI and INDIGO expect.

    Returns
    -------
    str
        The current timestamp.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

def print_msg(msg: str) -> None:
    """
    Prints a message to the standard error output. Should be used
    in Drivers to print some messages that should not be sent to the 
    clients.

    Parameters
    ----------
    msg : str
        The message to be printed.
    """
    print(msg, file=sys.stderr)
