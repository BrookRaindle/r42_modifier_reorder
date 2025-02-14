from PySide2.QtWidgets import QApplication, QMessageBox
from pymxs import runtime as rt
import sys
from site import addsitedir

addsitedir(r"Z:\_TEMP\Brook\3dsMax_Reorder_tool\r42_modifier_reorder")

from importlib import reload
import r42_modifier_reorder_ui

reload(r42_modifier_reorder_ui)

FFD_Filter = ["FFD 4x4x4", "FFD 3x3x3", "FFD 2x2x2", "FFDBox", "FFDCyl"]


class MainWindow(r42_modifier_reorder_ui.ModifierReorderUI):
    def __init__(self):
        super().__init__()
        self.selected_objects = []
        # Connections
        self.populate_button.clicked.connect(self.populate_modifiers)
        self.apply_button.clicked.connect(self.apply_load_order)
        self.undo_button.clicked.connect(undo_changes)

    def populate_modifiers(self):
        self.modifier_list.clear()
        self.selected_objects = list(rt.selection)
        if not self.selected_objects:
            QMessageBox.warning(
                self, "No Selection", "Please select at least one object"
            )
            return

        unique_modifiers = []
        self.object_dict = {}

        for obj in self.selected_objects:
            if not is_instanced(obj):
                modifiers = [mod.name for mod in obj.modifiers]
                for mod_name in modifiers:
                    if mod_name not in unique_modifiers:
                        unique_modifiers.append(mod_name)
                        self.modifier_list.addItem(mod_name)

                obj_data = {"object_name": obj.name, "mods": {}, "object": obj}
                for mod in obj.modifiers:
                    if mod.name not in obj_data["mods"]:
                        obj_data["mods"][mod.name] = []

                    obj_data["mods"][mod.name].append(mod)

                self.object_dict[obj.name] = obj_data

    def apply_load_order(self):
        total_mods = self.total_progress()
        if total_mods == 0:
            return

        # Store current file state
        rt.holdMaxFile()

        dialog, progress_bar = self.show_progress_dialog(
            total_mods=total_mods,
            title="Applying Load Order",
            message="Reordering modifiers...",
        )
        self.processed_mods = 0

        load_order = [
            self.modifier_list.item(i).text()
            for i in range(self.modifier_list.count())
        ]
        reversed(load_order)

        for obj_name, obj_data in self.object_dict.items():
            self.process_object(obj_name, load_order)

        rt.redrawViews()

        QMessageBox.information(
            self, "Success", "Modifiers reordered successfully"
        )
        self.populate_modifiers()

    def process_object(self, object_name, load_order):
        obj_dict_entry = self.object_dict.get(object_name)
        obj = self.object_dict.get(object_name, {}).get("object")
        mods = obj_dict_entry.get("mods", {})
        for target in load_order:
            if target in mods:
                modifiers = mods[target]
                for mod in modifiers:
                    if mod.name in FFD_Filter:
                        self.handle_FFD(obj, mod)

                    elif is_instanced(mod):
                        self.instance_modifier(obj, mod)

                    else:
                        self.copy_modifier(obj, mod)

    def instance_modifier(self, obj, mod):
        rt.addModifierWithLocalData(
            obj, mod, obj, mod, before=len(obj.modifiers)
        )
        rt.deleteModifier(obj, mod)

        self.processed_mods += 1
        self.update_progress_bar(self.processed_mods)
        QApplication.processEvents()
        return obj.modifiers[-1]

    def copy_modifier(self, obj, mod):
        rt.addModifierWithLocalData(
            obj, rt.copy(mod), obj, mod, before=len(obj.modifiers)
        )
        rt.deleteModifier(obj, mod)

        self.processed_mods += 1
        self.update_progress_bar(self.processed_mods)
        QApplication.processEvents()

    def handle_FFD(self, obj, mod):
        mod_context = {
            "TM": rt.getModContextTM(obj, mod),
            "BBoxMin": rt.getModContextBBoxMin(obj, mod),
            "BBoxMax": rt.getModContextBBoxMax(obj, mod),
        }
        cloned_mod = self.instance_modifier(obj, mod)
        rt.setModContextTM(obj, cloned_mod, mod_context["TM"])
        rt.setModContextBBox(
            obj, cloned_mod, mod_context["BBoxMin"], mod_context["BBoxMax"]
        )


def is_instanced(modifier):
    return rt.refhierarchy.IsRefTargetInstanced(modifier)


def undo_changes():
    rt.fetchMaxFile()


if __name__ == "__main__":
    app = QApplication.instance()
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())
