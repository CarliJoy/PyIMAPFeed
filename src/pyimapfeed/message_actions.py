"""
This file defines functions that perform actions with a single mail
message
"""
from typing import Dict


def get_actions_with_labels() -> Dict[str, str]:
    """
    Function that returns all
    TODO Implement properly
    """
    return {
        "none": "Nothing",
        "read": "Only mark message as read",
        "archive": "Archive to disk",
        "delete": "Delete message",
        "sort": "Sort message to folder",
    }
