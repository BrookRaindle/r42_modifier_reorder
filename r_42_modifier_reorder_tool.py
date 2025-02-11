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

    def populate_modifiers(self):
        # Clear the modifier list UI
        self.modifier_list.clear()
        self.selected_objects = list(rt.selection)
        if not self.selected_objects:
            QMessageBox.warning(self, "No Selection", "Please select at least one object")
            return
        
        unique_modifiers = []

        self.object_dict = {}
        for obj in self.selected_objects:
            modifiers = [mod.name for mod in obj.modifiers]
            for mod_name in modifiers:
                if mod_name not in unique_modifiers:
                    unique_modifiers.append(mod_name)
            # Create a dictionary entry for the current object
            obj_data = {
                "object_name": obj.name,
                "mods": {},  
                "object": obj
            }

            for mod in obj.modifiers:
                if mod.name not in obj_data["mods"]:        # checking to see if an object has already acknowledged a mod
                    obj_data["mods"][mod.name] = []         # initialises the mod entry if not (uses array since targetting wont matter)
                
                obj_data["mods"][mod.name].append(mod)      # adds duplicated

            self.object_dict[obj.name] = obj_data

        for mod_name in sorted(unique_modifiers):
            self.modifier_list.addItem(mod_name)
        
        # Debugging: Print the created dictionary to the console
        print("object_dict:")
        print(self.object_dict)

    def apply_load_order(self):
        load_order = [self.modifier_list.item(i).text() for i in range(self.modifier_list.count())]
        load_order.reverse()
        print(f"Desired Load Order: {load_order}")
        for obj_name, obj_data in self.object_dict.items():
            print(f"Processing Object {obj_name}")
            print(f"Modifiers for {obj_name}: {list(obj_data['mods'].keys())}")
            self.process_object(obj_name, load_order)
            rt.redrawViews()
        QMessageBox.information(self, "Success", "Modifiers reordered successfully")

        
        
    def process_object(self, object_name, load_order):
        obj_dict_entry = self.object_dict.get(object_name)
        obj = self.object_dict.get(object_name, {}).get('object')
        mods = obj_dict_entry.get("mods", {})
        for target in load_order:
            if target in mods:
                modifiers = mods[target]
                print(modifiers)
                for mod in modifiers:
                    if mod.name in FFD_Filter:
                        self.handle_FFD(obj=obj, mod=mod)
                    else:
                        self.clone_mod(obj=obj, mod=mod)

    def clone_mod(self, obj, mod) -> rt.modifier:
        cloned_mod = rt.copy(mod)
        rt.deleteModifier(obj, mod)
        rt.addModifier(obj, cloned_mod)
        print(f"Successfully handled! {cloned_mod}")
        return cloned_mod

    def handle_FFD(self, obj, mod):
        mod_context = {
                                "TM": rt.getModContextTM(obj, mod),
                                "BBoxMin": rt.getModContextBBoxMin(obj, mod),
                                "BBoxMax": rt.getModContextBBoxMax(obj, mod)}
        cloned_mod =self.clone_mod(obj, mod)
        rt.setModContextTM(obj, cloned_mod, mod_context["TM"])
        rt.setModContextBBox(obj, cloned_mod, mod_context["BBoxMin"], mod_context["BBoxMax"])
        

if __name__ == "__main__":
    app = QApplication.instance()
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())

#Code Written by Brook