import maya.cmds as cmds
import os


import utilitis
from utilitis import *


class FilepathNode(object):
    """
            Object that contains the infos a node has to have to be querried by farminizer to get the necessary data from the scene
    """
    __slots__ = ['node_name',
     'node_attributes',
     'node_attribute_value',
     'complete_attribute_name',
     'node_options',
     'path_is_relative']

    def __init__(self, node_name, node_attributes, node_attribute_value = '', node_options = False):
        self.node_name = node_name
        self.node_attributes = node_attributes
        self.complete_attribute_name = self.node_name + '.' + '.'.join(node_attributes)
        self.node_attribute_value = node_attribute_value
        self.node_options = node_options
        self.path_is_relative = False

    def is_node_data_valid(self):
        if not self.node_name:
            return False
        if not self.node_attributes:
            return False
        if not self.complete_attribute_name:
            return False
        if not self.node_attribute_value:
            return False
        return True


class SceneFiles:
    """
            get all attributes with file paths in them to
    """

    def __init__(self):
        self.all_file_path_nodes = list()
        self.get_all_filepath_attributes_from_scene()

    def is_attribute_string(self, attribute_name):
        """
                checks if attribute is a string
        """
        try:
            return cmds.getAttr(attribute_name, type=True) == 'string'
        except:
            return False

    def is_sub_attribute_a_string(self, node_name, node_attributes):
        """
                checks on list like attributes iterates through them and adds them if found
        """
        node_attribute_list = list()
        multi_node = node_name
        for attribute in node_attributes:
            multi_node += '.' + attribute
            node_attribute_list = cmds.getAttr(multi_node, multiIndices=True)
            if node_attribute_list != None:
                if len(node_attribute_list) == 0:
                    return False
                multi_node += '[' + str(node_attribute_list[0]) + ']'
            else:
                return False

        multi_node += '.' + node_attributes[len(node_attributes) - 1]
        return self.is_attribute_string(multi_node)

    def get_sub_attributes(self, node_data, index, node_name = ''):
        """
                gets all subattribute values, checks on list like attributes
        """
        node_name = node_name or node_data.node_name
        node_data.complete_attribute_name = node_name + '.' + node_data.node_attributes[index]
        if index == len(node_data.node_attributes) - 1:
            node_data.node_attribute_value = cmds.getAttr(node_data.complete_attribute_name)
            self.all_file_path_nodes.append(node_data)
            return
        attributes_list = cmds.getAttr(node_data.complete_attribute_name, multiIndices=True)
        for i in range(len(attributes_list)):
            partial_node_name_with_index = node_data.complete_attribute_name + '[' + attributes_list[i] + ']'
            self.get_sub_attributes(node_data, index + 1, partial_node_name_with_index)

    def get_string_attributes_from_node(self, scene_item):
        """
                iterates through all Attributes of a node if attribute is a path
                distinguishes between nodes with single attributes and nodes with several subattributes e.g. node.attribute.subattribute.subattribute
        """
        filename_attributes = cmds.listAttr(scene_item, usedAsFilename=True)
        if filename_attributes is not None:
            import sys
            if sys.version_info[0] >= 3:
                unicode = str
            filepath_types = ''
            ignored_node_attributes = ['sys_memory_tracking_output_path', 'fileNames']
            for index, item_attribute in enumerate(filename_attributes):
                node_attributes = item_attribute.split('.')
                complete_node_name = scene_item + '.' + item_attribute
                node_attribute_values = list()
                if len(node_attributes) < 2:
                    if item_attribute not in ignored_node_attributes and cmds.getAttr(complete_node_name, type=True) in filepath_types:
                        node_attribute_values.append(cmds.getAttr(complete_node_name))
                        for node_attribute_value in node_attribute_values:
                            if os.path.exists(node_attribute_value) and not self.path_already_in_another_node(node_attribute_value):
                                parsed_node_attribute_value = node_attribute_value
                                if cmds.attributeQuery('useFrameExtension', node=scene_item, exists=True) and cmds.getAttr(scene_item + '.useFrameExtension') == True:
                                    parsed_node_attribute_value = utilitis.parseSequence(node_attribute_value)
                                node_data = FilepathNode(scene_item, node_attributes, node_attribute_value)
                                if complete_node_name and node_attribute_value:
                                    if self.file_exists(parsed_node_attribute_value):
                                        node_data.path_is_relative = self.is_path_relative(node_attribute_value)
                                        self.all_file_path_nodes.append(node_data)
                                    elif self.is_dir_and_exists(node_attribute_value):
                                        pass

                else:
                    node_attribute_value = ''
                    node_data = FilepathNode(scene_item, node_attributes, node_attribute_value)
                    if self.is_sub_attribute_a_string(scene_item, node_attributes):
                        self.get_sub_attributes(node_data, index)

        return

    def get_all_filepath_attributes_from_scene(self):
        """
                Gets all nodes in Scene. Iterates through them
        """
        all_scene_nodes = cmds.ls()
        for scene_item in all_scene_nodes:
            print scene_item
            if cmds.objectType(scene_item) == 'cacheFile':
                continue
            self.get_string_attributes_from_node(scene_item)

    def is_path_relative(self, filepath, check_file = True):
        workspace_path = cmds.workspace(query=True, rootDirectory=True)
        path = os.path.normpath(os.path.join(workspace_path, filepath))
        if check_file:
            return os.path.isfile(path)
        else:
            return os.path.isdir(path)

    def file_exists(self, filepath):
        return os.path.isfile(filepath) or self.is_path_relative(filepath)

    def is_dir_and_exists(self, filepath):
        return os.path.isdir(filepath) or self.is_path_relative(filepath, check_file=False)

    def path_already_in_another_node(self, path_value):
        for node in self.all_file_path_nodes:
            if path_value in node.node_attribute_value:
                return True

        return False
