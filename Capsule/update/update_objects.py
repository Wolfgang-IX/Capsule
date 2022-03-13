
import bpy, bmesh, time
from math import *

from ..tk_utils import search as search_utils
from ..tk_utils import select as select_utils

# OBJECT DATA PROXY PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////

def FindEditableObjects(context):
    """
    Finds objects that can have their values edited.
    """
    collected = [] 

    for item in context.selected_objects:
        if item.CAPObj.enable_edit is True:
            collected.append(item)

    return collected

def CAP_Update_ProxyObjectExport(self, context):
    """
    Updates the selected objects "Enable Export" status across UI elements.
    Note - This should only be used from the Enable Export UI tick, otherwise manually handle "Enable Export" status 
    assignment using "UpdateObjectList"
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_enable_export

    # Run through any collected objects to also update them.
    for item in collected:
        item.CAPObj.enable_export = value
        UpdateObjectList(context.scene, item, value)


    return None


def CAP_Update_ProxyObjectOriginPoint(self, context):
    """
    Updates the "Use Scene Origin" property for all selected objects.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_origin_point

    # Run through the objects
    for item in collected:
        item.CAPObj.origin_point = value

    return None

def  CAP_Update_ProxyObjectLocationPreset(self, context):
    """
    Updates the object's Location Default property.
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy

    # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_location_preset

    # Run through the objects
    for item in collected:
        item.CAPObj.location_preset = value

    return None

def CAP_Update_ProxyObjectExportPreset(self, context):
    """
    Updates the object's Export Default property.
    """
    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
    proxy = context.scene.CAPProxy
    
     # If updates are disabled, return early.
    if proxy.disable_updates == True:
        return

    # Setup initial targets and the value state we need to change.
    collected = FindEditableObjects(context)
    value = proxy.obj_export_preset

    # Run through the objects
    for item in collected:
        item.CAPObj.export_preset = value

    return None


def CAP_Update_ActionItemName(self, context):
    """
    Updates an animation actions name when edited from a list.
    """
    active = context.active_object
    #print(">>> Changing Action Name <<<")
    #print(">>> Changing Action Name <<<")

    if active.animation_data is not None:
        animData = active.animation_data
        #print("Checking Object Animation Names...")

        if animData.action is not None:
            if animData.action.name == self.prev_name:
                animData.action.name = self.name
                self.prev_name = self.name
                return None

        for nla in active.animation_data.nla_tracks:
            #print("Checking NLA...", nla, nla.name)
            if nla.name == self.prev_name:
                nla.name = self.name
                self.prev_name = self.name
                return None

    modType = {'ARMATURE'}

    for modifier in active.modifiers:
        if modifier.type in modType:
            armature = modifier.object

    if armature is not None:
        if armature.animation_data is not None:
            animData = armature.animation_data
            #print("Checking Armature Animation Names...")

            if animData.action is not None:
                if animData.action.name == self.prev_name:
                    animData.action.name = self.name
                    self.prev_name = self.name
                    return None

            for nla in animData.nla_tracks:
                if nla.name == self.prev_name:
                    nla.name = self.name
                    self.prev_name = self.name
                    return None

    #print("No name could be changed for action", self.prev_name, ".  Oh no!")



# OBJECT LIST PROPERTIES
# /////////////////////////////////////////////////
# /////////////////////////////////////////////////


def UpdateObjectList(scene, object, enableExport):
    """
    Used when properties are updated outside the scope of the Export List
    to ensure that all UI elements are kept in sync.
    """
    scn = scene.CAPScn
    #print("Hey, this object is %s" % object)

    if object is None:
        return

    # Check a list entry for the object doesn't already exist.
    for item in scene.CAPScn.object_list:
        if item.object.name == object.name:
            #print("Changing", object.name, "'s export from list.'")
            item.enable_export = enableExport
            return

    # If an entry couldn't be found in the list, add it.
    if enableExport is True:
        #print("Adding", object.name, "to list.")
        entry = scn.object_list.add()
        entry.object = object
        entry.enable_export = enableExport

        object.CAPObj.in_export_list = True

    return None

def CAP_Update_FocusObject(self, context):
    """
    Focuses the camera to a particular object, ensuring the object is clearly within the camera frame.  
    """

    preferences = context.preferences
    addon_prefs = preferences.addons['Capsule'].preferences
            
    bpy.ops.object.select_all(action= 'DESELECT')
    select_utils.SelectObject(self.object)

    # As the context won't be correct when the icon is clicked
    # We have to find the actual 3D view and override the context of the operator
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 
                                'region': region, 
                                'edit_object': bpy.context.edit_object, 
                                'scene': bpy.context.scene, 
                                'screen': bpy.context.screen, 
                                'window': bpy.context.window}

                    bpy.ops.view3d.view_selected(override)
    return None


def CAP_Update_SelectObject(self, context):
    """
    Selects (but doesn't focus) the given object.
    """

    bpy.ops.object.select_all(action= 'DESELECT')
    select_utils.ActivateObject(self.object)
    select_utils.SelectObject(self.object)

    return None



def CAP_Update_ObjectListExport(self, context):
    """
    Updates the "Enable Export" object status once changed from the list menu.
    Note - Do not use this in any other place apart from when an object is represented in a list.
    """

    #print("Changing Enable Export... (List)")  
    self.object.CAPObj.enable_export = self.enable_export
    
    # TODO / WARNING
    # If the object is the active selection we should really change the proxy so it fits right?
    proxy = context.scene.CAPProxy



    return None


def CAP_Update_ObjectListRemove(self, context):
    """
    Used in a list to remove an object from both the export list, while disabling it's "Enable Export" status.
    """
    #print("-----DELETING OBJECT FROM LIST-----")
    
    scn = context.scene.CAPScn
    object_list = context.scene.CAPScn.object_list

    # To avoid issues within the list, the selected list item needs to be preserved.
    backupListIndex = scn.object_list_index
    backupListLength = len(object_list)

    # TODO: Ensure it can handle deleted objects!

    # Remove it as an export candidate
    if self.object != None:
        self.object.CAPObj.enable_export = False
        self.object.CAPObj.in_export_list = False
    
    # Find the index and remove it from the list
    # TODO: There's probably a more efficient way right?
    i = None
    try:
        i = object_list.values().index(self)
        object_list.remove(i)

    except ValueError:
        return
    
    # If the index is more than the list, bring it down one
    if scn.object_list_index > i:
        scn.object_list_index -= 1

    return
                

            
