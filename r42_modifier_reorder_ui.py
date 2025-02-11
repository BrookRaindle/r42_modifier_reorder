from PySide2.QtWidgets import (
    QMainWindow,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide2.QtCore import Qt


class ModifierReorderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modifier Reorder Tool")
        self.setGeometry(100, 100, 400, 600)

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # List widget to display modifiers
        self.modifier_list = QListWidget()
        self.modifier_list.setSelectionMode(QListWidget.SingleSelection)
        self.modifier_list.setDragDropMode(QListWidget.InternalMove)  # Enable drag-and-drop
        self.layout.addWidget(self.modifier_list)

        # Button to populate the list
        self.populate_button = QPushButton("Populate Modifiers")
        self.layout.addWidget(self.populate_button)

        # Button to apply the new order
        self.apply_button = QPushButton("Apply Load Order")
        self.layout.addWidget(self.apply_button)


        