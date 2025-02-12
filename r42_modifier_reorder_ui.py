from PySide2.QtWidgets import (
    QMainWindow,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QDialog,
    QLabel
)
from PySide2.QtCore import Qt

class ModifierReorderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("R42 Modifier Reorder Tool")
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
        self.populate_button = QPushButton("Populate Modifiers From Selected Objects")
        self.layout.addWidget(self.populate_button)

        # Button to apply the new order
        self.apply_button = QPushButton("Apply Load Order")
        self.layout.addWidget(self.apply_button)


    def show_progress_dialog(self, total_mods, title="Processing...", message="Please wait..."):

        self.dialog = QDialog(self)
        self.dialog.setWindowTitle(title)
        #dialog.setModal(True)  # Make it modal (blocks interaction with the main window)
        dialog_layout = QVBoxLayout(self.dialog)
        label = QLabel(message)
        dialog_layout.addWidget(label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(total_mods)
        self.progress_bar.setValue(0)
        dialog_layout.addWidget(self.progress_bar)
        
        # Show the dialog
        self.dialog.show()
        return self.dialog, self.progress_bar

    def total_progress(self):
        total_mod_count = 0
        for obj_name, obj_data in self.object_dict.items():
            for mod_name, mod_instances in obj_data["mods"].items():
                total_mod_count += len(mod_instances)
        print(f"Total Mods Across All Objects: {total_mod_count}")
        return total_mod_count 
    
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
        if self.progress_bar.value() == self.progress_bar.maximum(): 
            self.dialog.close()