from enum import unique
from PySide2.QtWidgets import QApplication, QMessageBox
from pymxs import runtime as rt
import sys
from site import addsitedir
import os

addsitedir(r"C:\Users\brook\Desktop\r42_modifier_reorder")

from importlib import reload
import r42_modifier_reorder_ui

reload(r42_modifier_reorder_ui)



FFD_Filter = ["FFD 4x4x4", "FFD 3x3x3", "FFD 2x2x2", "FFDBox", "FFDCyl"]



class MainWindow(r42_modifier_reorder_ui.ModifierReorderUI):
    def __init__(self):
        super().__init__()
        self.populate_button.clicked.connect(self.populate_modifiers)
        self.apply_button.clicked.connect(self.apply_load_order)
        self.selected_objects = []
        self.original_modifier_orders = {}

    def populate_modifiers(self):
        
        self.modifier_list.clear()
        self.selected_objects = list(rt.selection)
        if not self.selected_objects:
            QMessageBox.warning(self, "No Selection", "Please select at least one object")
            return

        #all unique modifiers
        unique_modifiers = set()

        for obj in self.selected_objects:
            modifiers = [mod.name for mod in obj.modifiers]
            unique_modifiers.update(modifiers)
            self.original_modifier_orders[obj.name] = modifiers  #Store original order
            print(f"Unique Modifiers: {unique_modifiers}")
        print(f"unique_modifiers: {unique_modifiers}")
        #Add modifiers to the list
        for mod_name in sorted(unique_modifiers):
            self.modifier_list.addItem(mod_name)

    def apply_load_order(self):
        new_load_order = [self.modifier_list.item(i).text() for i in range(self.modifier_list.count())]
        # Reverse the load order to account for bottom-up placement
        new_load_order = reversed(new_load_order)
        print(f"Desired Load Order: {new_load_order}")

        for obj in self.selected_objects:
        # Create a temporary list to hold the new modifier stack
            temp_modifiers = []

            # Process modifiers in desired load order
            for target in new_load_order:
                for mod in obj.modifiers:
                    if mod.name == target:
                        if mod.name not in FFD_Filter:
                            # Clone non-FFD modifiers and add them to the temp list
                            cloned_mod = rt.copy(mod)
                            temp_modifiers.append(cloned_mod)
                        elif mod.name in FFD_Filter:
                            # Preserve FFD local data and add to the temp list
                            mod_context = {
                                "TM": rt.getModContextTM(obj, mod),
                                "BBoxMin": rt.getModContextBBoxMin(obj, mod),
                                "BBoxMax": rt.getModContextBBoxMax(obj, mod),
                            }
                            temp_modifiers.append((mod, mod_context))

            # Clear the existing modifier stack
            for item in temp_modifiers:
                if isinstance(item, tuple):  # FFD modifier with context
                    mod, context = item
                    # Clone the FFD modifier instead of using the original
                    cloned_mod = rt.copy(mod)
                    rt.addModifier(obj, cloned_mod)  # Add the cloned modifier to the stack
                    rt.setModContextTM(obj, cloned_mod, context["TM"])
                    rt.setModContextBBox(obj, cloned_mod, context["BBoxMin"], context["BBoxMax"])
                else:  # Non-FFD modifier
                    rt.addModifier(obj, item)
            while len(obj.modifiers) > len(temp_modifiers):
                rt.deleteModifier(obj, obj.modifiers[-1])


                rt.redrawViews()
        QMessageBox.information(self, "Success", "Modifiers reordered successfully")


if __name__ == "__main__":
    app = QApplication.instance()
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())