from typing import List

from imap_tools import MailBox, MailMessage

import pyimapfeed.constants as const
from pyimapfeed.config import InternalIMAPServerConfig


class ImapMailBox(MailBox):
    def __init__(self, config: InternalIMAPServerConfig):
        super().__init__(config.server)
        self.login(config.user, config.password)

    def get_gui_folders(self) -> List[str]:
        return list(
            sorted(
                folder.name.replace(folder.delim, const.GUI_FOLDER_DELIM)
                for folder in self.folder.list()
            )
        )

    def get_mails(self) -> List[MailMessage]:
        """
        Currently only a fast wrapper to get some mails

        in the future we want to combine this with a cache that
        loads only new mails
        """
        return list(
            self.fetch(
                mark_seen=False,
                headers_only=True,
                bulk=True,
                limit=20,
                charset="UTF8",
                reverse=True,
            )
        )
