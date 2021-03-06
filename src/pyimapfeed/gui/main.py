import importlib.resources as pkg_resources
import sys
from typing import Dict

from imap_tools import MailMessage
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDesktopWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)

from pyimapfeed import constants as const
from pyimapfeed import resources
from pyimapfeed.config import get_full_server_config, get_server_configs
from pyimapfeed.gui.fonts import HEADER_FONT
from pyimapfeed.gui.widgets import MailTable, RadioGroup
from pyimapfeed.imap import ImapMailBox
from pyimapfeed.mail_helper import get_html_display
from pyimapfeed.message_actions import get_actions_with_labels


class MainWindow(QWidget):
    # Settings
    imap_connection: ImapMailBox

    # Shortcuts
    shortcut_close: QShortcut

    # Layout Elements
    layout_main_window: QHBoxLayout
    layout_main_message: QVBoxLayout
    layout_main_action: QVBoxLayout

    # Message Widgets
    message_view: QWebEngineView
    message_selection: MailTable

    # Action Widgets
    label_action_heading: QLabel
    message_priority_radios: RadioGroup
    message_action_radios: RadioGroup
    btn_perform_action: QPushButton
    dropdown_folders: QComboBox

    # Make used constants part of the class, for easier interfacing
    MESSAGE_PRIORITIES: Dict[int, str] = const.MESSAGE_PRIORITIES

    def __init__(self, mailbox: ImapMailBox):
        super().__init__()
        self.imap_connection = mailbox
        self.setWindowTitle(const.GUI_WINDOW_NAME)

        # Create all the widgets we need
        self.message_view = QWebEngineView()
        self.message_selection = MailTable()
        self.dropdown_folders = QComboBox()
        self.dropdown_folders.addItems(self.imap_connection.get_gui_folders())

        self.label_action_heading = QLabel(const.GUI_ACTION_HEADER)
        self.label_action_heading.setFont(HEADER_FONT)
        self.btn_perform_action = QPushButton(const.GUI_BUTTON_PERFORM_ACTION)
        self.btn_perform_action.clicked.connect(self.do_perform_and_go_next)

        # Create Main Window Layout
        self.layout_main_window = QHBoxLayout()

        self.layout_main_message = QVBoxLayout()
        self.layout_main_action = QVBoxLayout()

        # Build main layout
        self.layout_main_window.addLayout(self.layout_main_message, 3)
        self.layout_main_window.addLayout(self.layout_main_action)

        # Create Message Layout
        self.layout_main_message.addWidget(self.message_selection, 10)
        self.layout_main_message.addWidget(self.message_view, 30)

        # Create the Action Layout
        self.layout_main_action.addWidget(self.label_action_heading)
        self.message_priority_radios = RadioGroup("Priority")
        for priority, label in self.MESSAGE_PRIORITIES.items():
            self.message_priority_radios.add_radio_button(label, priority)

        self.layout_main_action.addWidget(self.message_priority_radios.box)

        self.message_action_radios = RadioGroup("Action")
        actions = get_actions_with_labels()
        for key, label in actions.items():
            self.message_action_radios.add_radio_button(label, key=key)
        self.layout_main_action.addWidget(self.message_action_radios.box)

        self.layout_main_action.addWidget(self.dropdown_folders)

        self.layout_main_action.addStretch()
        self.layout_main_action.addWidget(self.btn_perform_action)

        # Set the layout on the application's window

        self.setLayout(self.layout_main_window)

        # print(self.children())

        # Define Shortcuts
        self.shortcut_close = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_close.activated.connect(self.do_quit_app)

        # Define Window Size and position
        self.resize(1024, 768)
        self.center_window()
        self.load_mails()
        self.message_selection.set_mail_selection_handler(self.display_mail)

    def load_mails(self):
        self.message_selection.add_mail_entries(self.imap_connection.get_mails())

    def display_mail(self, mail: MailMessage):
        self.message_view.setHtml(get_html_display(mail))

    def center_window(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def do_perform_and_go_next(self):
        print(f"Action: {self.message_action_radios.get_selected().__repr__()}")
        print(f"Priority: {self.message_priority_radios.get_selected().__repr__()}")

    def do_quit_app(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    css = pkg_resources.read_text(resources, "Qapp.css")
    app.setStyleSheet(css)
    # TODO create a widget to enter passwords and server
    #      for the moment to debug, we only use the settings existing
    configs = get_server_configs()
    if not configs:
        raise NotImplementedError(
            "Could not load any server config, creating new ones "
            "is not supported at the moment"
        )
    # TODO a Selection on Multiple server should be shown
    config = next(configs.values().__iter__())
    # TODO create a ask for Password Dialog
    config = get_full_server_config(config)
    with ImapMailBox(config) as imap_connection:
        window = MainWindow(imap_connection)
        window.show()
    sys.exit(app.exec_())
