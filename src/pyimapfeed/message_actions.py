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
        "none": "n&othing",
        "read": "only mark message as &read",
        "archive": "&archive to disk",
        "delete": "&delete message",
        "sort": "&move message to folder",
    }
