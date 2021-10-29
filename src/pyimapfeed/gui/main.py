import importlib.resources as pkg_resources
import sys
from typing import Dict, Optional, Union

from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from pyimapfeed import constants as const
from pyimapfeed import resources
from pyimapfeed.gui.fonts import HEADER_FONT
from pyimapfeed.message_actions import get_actions_with_labels

RadioKey = Union[str, int]


class RadioGroup:
    """
    Visible Representation of a Radio Box,

    helps to keep an order with Radio Boxes without having to think
    about them too much
    """

    box: QGroupBox
    layout: QLayout
    button_group: QButtonGroup
    radios: Dict[RadioKey, QRadioButton]
    _id_to_key_mapping: Dict[int, RadioKey]

    def __init__(self, label: str, layout: Optional[QLayout] = None):
        self.box = QGroupBox(label)
        if layout is None:
            layout = QVBoxLayout()
        self.layout = layout
        self.box.setLayout(self.layout)
        self.button_group = QButtonGroup()
        self.radios = {}
        self._id_to_key_mapping = {}

    def add_radio_button(
        self, label: str, id_: Optional[int] = None, key: Optional[RadioKey] = None
    ) -> QRadioButton:
        """
        Simply add a Radio Button to the Group

        Args:
            label: The user visible radio button
            id_: the id used with the QButtonGroup, if None
                 it will be auto generated by QButtonGroup
            key: An key used to identify the radio button, if None
                 the id_ will be used

        Returns:
            The created Radio button
        """

        radio_button = QRadioButton(label)
        if id_ is not None:
            self.button_group.addButton(radio_button, id_)
        else:
            self.button_group.addButton(radio_button)
            id_ = self.button_group.id(radio_button)
        if key is None:
            key = id_
        self._id_to_key_mapping[id_] = key
        self.layout.addWidget(radio_button)
        return radio_button

    def get_selected(self) -> Optional[RadioKey]:
        return self._id_to_key_mapping.get(self.button_group.checkedId())


class Window(QWidget):
    # Layout Elements
    main_window_layout: QHBoxLayout
    main_message_layout: QVBoxLayout
    main_action_layout: QVBoxLayout

    # Message Widgets
    message_view: QTextBrowser
    message_selection: QTableWidget

    # Action Widgets
    action_heading_label: QLabel
    message_priority_radios: RadioGroup
    message_action_radios: RadioGroup
    perform_action_btn: QPushButton

    # Make used constants part of the class, for easier interfacing
    MESSAGE_PRIORITIES: Dict[int, str] = const.MESSAGE_PRIORITIES

    def __init__(self):

        super().__init__()
        self.setWindowTitle(const.GUI_WINDOW_NAME)

        # Create all the widgets we need
        self.message_view = QTextBrowser()
        self.message_selection = QTableWidget(10, 5)

        self.action_heading_label = QLabel(const.GUI_ACTION_HEADER)
        self.action_heading_label.setFont(HEADER_FONT)
        self.perform_action_btn = QPushButton(const.GUI_BUTTON_PERFORM_ACTION)

        # Create Main Window Layout
        self.main_window_layout = QHBoxLayout()

        self.main_message_layout = QVBoxLayout()
        self.main_action_layout = QVBoxLayout()

        # Build main layout
        self.main_window_layout.addLayout(self.main_message_layout, 3)
        self.main_window_layout.addLayout(self.main_action_layout)

        # Create Message Layout
        self.main_message_layout.addWidget(self.message_selection, 10)
        self.main_message_layout.addWidget(self.message_view, 30)

        # Create the Action Layout
        self.main_action_layout.addWidget(self.action_heading_label)
        self.message_priority_radios = RadioGroup("Priority")
        for priority, label in self.MESSAGE_PRIORITIES.items():
            self.message_priority_radios.add_radio_button(label, priority)

        self.main_action_layout.addWidget(self.message_priority_radios.box)

        self.message_action_radios = RadioGroup("Action")
        actions = get_actions_with_labels()
        for key, label in actions.items():
            self.message_action_radios.add_radio_button(label, key=key)
        self.main_action_layout.addWidget(self.message_action_radios.box)

        self.main_action_layout.addStretch()
        self.main_action_layout.addWidget(self.perform_action_btn)

        # Set the layout on the application's window

        self.setLayout(self.main_window_layout)

        # print(self.children())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    css = pkg_resources.read_text(resources, "Qapp.css")
    print(css)
    app.setStyleSheet(css)
    window = Window()
    window.show()
    sys.exit(app.exec_())
