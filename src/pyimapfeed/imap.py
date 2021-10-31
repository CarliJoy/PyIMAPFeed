from typing import List

from imap_tools import MailBox

import pyimapfeed.constants as const
from pyimapfeed.config import InternalIMAPServerConfig


def get_folders(config: InternalIMAPServerConfig) -> List[str]:
    with MailBox(config.server).login(config.user, config.password) as mailbox:
        return list(
            sorted(
                folder.name.replace(folder.delim, const.GUI_FOLDER_DELIM)
                for folder in mailbox.folder.list()
            )
        )
