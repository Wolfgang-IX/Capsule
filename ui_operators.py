import bpy, bmesh
from bpy.types import Operator
from .definitions import SelectObject, FocusObject, ActivateObject, DuplicateObject, DuplicateObjects, DeleteObject, MoveObject, MoveObjects, CheckSuffix
from mathutils import Vector

#///////////////// - LOCATION DEFAULTS - ///////////////////////////////////////////

class GX_Add_Path(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addpath"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        newPath = scn.location_defaults.add()
        newPath.name = "Location " + str(len(scn.location_defaults))
        newPath.path = ""

        # Position the index to the current location of the
        #count = 0
        #for i, item in enumerate(scn.path_defaults, 1):
            #count += 1

        #oldIndex = scn.path_list_index

        #scn.path_defaults.move(count - 1, scn.path_list_index)
        #scn.path_list_index = oldIndex

        return {'FINISHED'}

class GX_Delete_Path(Operator):
    """Deletes the selected path from the menu"""

    bl_idname = "scene.gx_deletepath"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        scn.location_defaults.remove(scn.location_defaults_index)

        return {'FINISHED'}



#///////////////// - EXPORT DEFAULTS - ///////////////////////////////////////////

class GX_Add_Export(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addexport"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences
        newDefault = addon_prefs.export_defaults.add()
        newDefault.name = "Export " + str(len(addon_prefs.export_defaults))
        newDefault.path = ""

        return {'FINISHED'}

class GX_Delete_Export(Operator):
    """Deletes the selected path from the menu"""

    bl_idname = "scene.gx_deleteexport"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences
        addon_prefs.export_defaults.remove(addon_prefs.export_defaults_index)

        return {'FINISHED'}

class GX_Add_Pass(Operator):
    """Creates a path from the menu"""

    bl_idname = "scene.gx_addpass"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences
        export = addon_prefs.export_defaults[addon_prefs.export_defaults_index]
        newPass = export.passes.add()
        newPass.name = "Pass " + str(len(export.passes))
        newPass.path = ""

        return {'FINISHED'}

class GX_Delete_Pass(Operator):
    """Deletes the selected path from the menu"""

    bl_idname = "scene.gx_deletepass"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences
        export = addon_prefs.export_defaults[addon_prefs.export_defaults_index]
        export.passes.remove(export.passes_index)

        export.passes_index -= 1

        return {'FINISHED'}

class GX_Shift_Path_Up(Operator):
    """Moves the current entry in the list up by one"""

    bl_idname = "scene.gx_shiftup"
    bl_label = "Add"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index - 1)
        scn.path_list_index -= 1

        return {'FINISHED'}

class GX_Shift_Path_Down(Operator):
    """Moves the current entry in the list down by one"""

    bl_idname = "scene.gx_shiftdown"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        scn.path_defaults.move(scn.path_list_index, scn.path_list_index + 1)
        scn.path_list_index += 1

        return {'FINISHED'}

#///////////////// - OBJECTS - //////////////////////////////////////////////////////
class GX_Refresh_Objects(Operator):
    """Generates a list of groups to browse"""

    bl_idname = "scene.gx_refobjects"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn

        scn.object_list.clear()

        for object in context.scene.objects:
            if object.GXObj.enable_export is True:
                entry = scn.object_list.add()
                entry.name = object.name
                entry.prev_name = object.name
                entry.enable_export = object.GXObj.enable_export


        return {'FINISHED'}


#///////////////// - GROUPS - //////////////////////////////////////////////////////


class GX_Refresh_Groups(Operator):
    """Generates a list of groups to browse"""

    bl_idname = "scene.gx_refgroups"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn

        scn.group_list.clear()

        for group in bpy.data.groups:
            groupEntry = scn.group_list.add()
            groupEntry.name = group.name
            groupEntry.prev_name = group.name


        return {'FINISHED'}

class GX_Set_Root_Object(Operator):
    """Lets you click on another object to set it as the root object for the group."""

    bl_idname = "scene.gx_setroot"
    bl_label = "Remove"

    def finish(self):
        # This def helps us tidy the shit we started
        # Restore the active area's header to its initial state.
        bpy.context.area.header_text_set()


    def execute(self, context):
        print("invoke!")
        print("Is this new?")

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        user_preferences = context.user_preferences
        self.addon_prefs = user_preferences.addons["GEX"].preferences

        self.object = context.scene.objects.active
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.05, context.window)

        bpy.ops.object.select_all(action='DESELECT')

        # Set the header text with USEFUL INSTRUCTIONS :O
        context.area.header_text_set(
            "Select the object you want to use as a root object.  " +
            "RMB: Select Collision Object, Esc: Exit"
        )

        return {'RUNNING_MODAL'}

    def CheckForChild(self, group, target):

        # Figure out if it is a child of any object in the group.
        print("Searching through children...")
        for altObject in group.objects:
            for child in altObject.children:
                print("Checking child ", child.name)
                if child.name == target.name:
                    self.report({'WARNING'}, 'The object selected is a child of another object in the group, and cant be used as a root object.')

                    FocusObject(self.object)
                    self.finish()
                    return{'FINISHED'}

    def modal(self,context,event):
        # If escape is pressed, exit
        if event.type in {'ESC'}:
            self.finish()

            # This return statement has to be within the same definition (cant defer to finish())
            return{'FINISHED'}

        # When an object is selected, set it as a child to the object, and finish.
        elif event.type == 'RIGHTMOUSE':

            # ALSO, check its not a dummy or origin object
            if context.selected_objects != None and len(context.selected_objects) == 1:

                entry = context.scene.GXScn.group_list[context.scene.GXScn.group_list_index]
                for group in bpy.data.groups:
                    if group.name == entry.name:

                        print("Found Group: ", group.name)
                        for object in group.objects:
                            if object.name == context.selected_objects[0].name:
                                if object.name.find(self.addon_prefs.lp_tag) != -1:
                                    print("Object Passed Main Check", object.name)

                                    self.CheckForChild(group, object)

                                    group.GXGrp.root_object = context.selected_objects[0].name
                                    FocusObject(self.object)
                                    self.finish()
                                    return{'FINISHED'}

                                elif group.GXGrp.auto_assign is False:

                                    self.CheckForChild(group, object)

                                    group.GXGrp.root_object = context.selected_objects[0].name
                                    FocusObject(self.object)
                                    self.finish()
                                    return{'FINISHED'}

                                else:
                                    self.report({'WARNING'}, 'The object selected is not a low-poly object, PAY ATTENTION OmO')

                                    FocusObject(self.object)
                                    self.finish()
                                    return{'FINISHED'}



                        self.report({'WARNING'}, 'The object selected is not in the same group, TRY AGAIN O_O')

                        FocusObject(self.object)
                        self.finish()
                        return{'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}


class GX_Clear_Root_Object(Operator):
    """Clears the currently chosen root object."""

    bl_idname = "scene.gx_clearroot"
    bl_label = "Remove"

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        obj = context.active_object.GXObj

        entry = context.scene.GXScn.group_list[context.scene.GXScn.group_list_index]
        for group in bpy.data.groups:
            if group.name == entry.name:
                group.GXGrp.root_object = ""
                return{'FINISHED'}

        return {'FINISHED'}


class GX_Reset_Scene(Operator):
    """Resets all object and group variables in the file."""

    bl_idname = "scene.gx_resetsceneprops"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        exportedObjects = 0

        # Keep a record of the selected and active objects to restore later
        active = None
        selected = []

        for sel in context.selected_objects:
            if sel.name != context.active_object.name:
                selected.append(sel)

        active = context.active_object

        for group in bpy.data.groups:
            group.GXGrp.export_group = False
            group.GXGrp.auto_assign = False
            group.GXGrp.location_default = '0'

        for object in bpy.data.objects:
            obj = object.GXObj
            FocusObject(object)

            obj.enable_export = False
            obj.apply_modifiers = False
            obj.triangulate = False
            obj.use_collision = False
            obj.generate_convex = False
            obj.separate_collision = False
            obj.collision_object = ""
            obj.export_collision = False
            obj.location_default = '0'
            obj.export_anim = False
            obj.export_anim_file = False
            obj.export_anim_actions = False

        # Re-select the objects previously selected
        FocusObject(active)

        for sel in selected:
            SelectObject(sel)

        return {'FINISHED'}

class GX_Reset_Scene(Operator):
    """Resets all location and export defaults in the file"""

    bl_idname = "scene.gx_resetprefs"
    bl_label = "Reset Scene"

    def execute(self, context):
        print(self)

        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["GEX"].preferences

        if addon_prefs == None:
            print("ADDON COULD NOT START, CONTACT DEVELOPER FOR ASSISTANCE")
            return

        # Figure out if an object already exists, if yes, DELETE IT
        for object in bpy.data.objects:
            print(object)
            if object.name == addon_prefs.default_datablock:
                DeleteObject(object)

        # Otherwise create the object using the addon preference data
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES')

        defaultDatablock = bpy.context.scene.objects.active
        defaultDatablock.name = addon_prefs.default_datablock
        defaultDatablock.hide = True
        defaultDatablock.hide_render = True
        defaultDatablock.hide_select = True


        return {'FINISHED'}

class GX_UI_Group_Separate(Operator):
    """Toggles the drop-down menu for separate group export options"""

    bl_idname = "scene.gx_grpseparate"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        ui = context.scene.GXUI

        if ui.group_separate_dropdown is True:
            ui.group_separate_dropdown = False
        else:
            ui.group_separate_dropdown = True

        return {'FINISHED'}

class GX_UI_Group_Options(Operator):
    """Toggles the drop-down menu for separate group export options"""

    bl_idname = "scene.gx_grpoptions"
    bl_label = ""

    def execute(self, context):
        print(self)

        scn = context.scene.GXScn
        ui = context.scene.GXUI

        if ui.group_options_dropdown is True:
            ui.group_options_dropdown = False
        else:
            ui.group_options_dropdown = True

        return {'FINISHED'}


class GX_Refresh_Actions(Operator):
    """Generates a list of groups to browse"""

    bl_idname = "scene.gx_refactions"
    bl_label = "Refresh"

    def execute(self, context):
        print(self)

        ui = context.scene.GXUI
        active = context.active_object
        armature = None

        ui.action_list.clear()

        if active.animation_data is not None:
            actions = active.animation_data.nla_tracks
            activeAction = active.animation_data.action

            if activeAction is not None:
                entry = ui.action_list.add()
                entry.name = activeAction.name
                entry.prev_name = activeAction.name
                entry.anim_type = '1'

            for action in actions:
                entry = ui.action_list.add()
                entry.name = action.name
                entry.prev_name = action.name
                entry.anim_type = '2'


        modType = {'ARMATURE'}

        for modifier in active.modifiers:
            if modifier.type in modType:
                armature = modifier.object

        if armature is not None:
            if armature.animation_data is not None:
                actions = armature.animation_data.nla_tracks
                activeAction = armature.animation_data.action

                if activeAction is not None:
                    entry = ui.action_list.add()
                    entry.name = activeAction.name
                    entry.prev_name = activeAction.name
                    entry.anim_type = '3'

                for action in actions:
                    entry = ui.action_list.add()
                    entry.name = action.name
                    entry.prev_name = action.name
                    entry.anim_type = '4'


        return {'FINISHED'}

class GX_Test_Me(Operator):

    """Dont fucking ask"""

    bl_idname = "scene.gx_teststuff"
    bl_label = "TEST ME"

    def execute(self, context):

        string = "_LP_LP"
        suffix = "_LP"

        print("First test...")
        CheckSuffix(string, suffix)

        string = "Cube_LPSUPERAWESOME_LP"
        suffix = "_LP"

        print("Second test...")
        CheckSuffix(string, suffix)

        string = "CubeDX"
        suffix = "_LP"

        print("Third test...")
        CheckSuffix(string, suffix)

        string = "PL_ebuC"
        suffix = "_LP"

        print("Final test...")
        CheckSuffix(string, suffix)

        return {'FINISHED'}
