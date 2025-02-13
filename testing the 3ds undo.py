#Attempt 1
from pymxs import runtime as rt

def is_object_instanced(obj):
    return rt.refhierarchy.IsRefTargetInstanced(obj)

selected_objects = []
selected_objects = list(rt.selection)
for obj in selected_objects:
    if is_object_instanced(obj):
        print(f"Object '{obj.name}' is instanced.")
    else: 
        print(f"Object '{obj.name}' is NOT instanced.")
   

#Attempt 2

#from pymxs import runtime as rt
#from pymxs import undo, run_undo
#
#selected_objects = []
#selected_objects = list(rt.selection)
#def do_with_undo():
#    for obj in selected_objects:
#        mod_copy = rt.copy(obj.modifiers[0])
#        rt.addModifier(obj, mod_copy)
#        rt.addModifier(obj, mod_copy)
#        rt.redrawViews()
#
#maxscript_code = """
#undo "Modifier Reorder Operation" on
#(
#    python.Execute("do_with_undo()")
#)
#"""
#
#rt.execute(maxscript_code)