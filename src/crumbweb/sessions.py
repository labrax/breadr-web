"""Store the different files open"""

import os
from typing import Dict


class FileState:
    """A file with its slice etc"""
    def __init__(self, filepath):
        self.slice = None
        self.node_counter = 0
        self.filepath = filepath
        self.mapping_id_element = {}  # maps UI node ids to the internal nodes
        self.bakery_items_available = {}  # from the locally-available files
        self.translation = (0, 0)
        self.zoom_level = 0
        self.node_position = {}

        if os.path.exists(filepath):
            self.load_from_file(filepath)
        else:
            pass

    def load_from_file(self, path):
        """Load a slice from a file"""
        # get any meta-data from crumb web
        # load every node
        # load every connection
        raise NotImplementedError

    def send_batch(self):
        """Dispatches the local definitions in a single dict"""
        raise NotImplementedError

    def refresh_list(self):
        """Reloads the list of functions available"""
        raise NotImplementedError

    def get_function_list(self):
        """Send the list of functions available"""
        self.refresh_list()
        sections = [{'name': 'Basics', 'code': 'basics',
                    'functions': [{'type_identifier': 'input_element', 'name': ' Input', 'icon': 'fa-solid fa-arrow-right-to-bracket'},
                                  {'type_identifier': 'output_element', 'name': ' Output', 'icon': 'fa-solid fa-arrow-right-from-bracket'}]},
                    {'name': 'Crumbs', 'code': 'crumbs',
                    'functions': [{'type_identifier': 'multiple_element', 'name': ' AAA', 'icon': 'fas fa-code'},
                                  {'type_identifier': 'multiple_element', 'name': ' BBB', 'icon': 'fas fa-code'},
                                  {'type_identifier': 'multiple_element', 'name': ' CCC', 'icon': 'fas fa-code'}]}
                    ]
        return sections

    def save(self):
        """Calls the slice to be saved"""
        raise NotImplementedError

    def setParameter(self, node: int, name: str, type: str):
        """Rename an input"""
        # check if we good changing? aka: anything connected here? no duplicates?
        raise NotImplementedError

    def run(self):
        """Run the output for all the nodes"""
        raise NotImplementedError

    def translate(self, x, y):
        """Sets the translation for this execution"""
        self.translation = (x, y)

    def zoom(self, z):
        """Sets the zoom for the element"""
        self.zoom_level = z

    def move_node(self, id, x, y):
        """Set a node position"""
        self.node_position[id] = (x, y)

    def addNode(self, name, pos_x, pos_y) -> dict:
        # if available, get it
        # add to slice
        # add to reference of nodes
        if name in self.bakery_items_available:
            ret = self.bakery_items_available[name]
        raise NotImplementedError
        self.node_position[name] = (pos_x, pos_y)
        self.mapping_id_element[self.node_counter] = NotImplemented  # slice new node
        self.node_counter += 1

    def removeNode(self, id):
        """Remove a node (if possible"""
        raise NotImplementedError

    def addConnection(self, id_output, id_input, output_class, input_class):
        """Adds a connection between two nodes (if possible)"""
        raise NotImplementedError

    def removeConnection(self, class_list):
        """Remove a connection between two nodes (if possible)"""
        raise NotImplementedError


class SessionStore:
    """All the stored sessions"""
    file_to_data: Dict[str, FileState] = {}

    @classmethod
    def get_file(cls, filepath):
        if filepath not in cls.file_to_data:
            cls.file_to_data[filepath] = FileState(filepath)
        return cls.file_to_data[filepath]
