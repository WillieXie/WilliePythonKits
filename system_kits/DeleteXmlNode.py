#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2019-12-4
# =============================================================================
"""
Reading invision_repo.xml <project> node `name` attribute:

       <project name="QCom8998/81/frameworks/base"/>

   Then delete the same <project> node in default.xml


"""

# =============================================================================
# Imports
# =============================================================================
import os
import re
import subprocess
import xml.etree.ElementTree as ET

dest_tree = ET.parse('default.xml')
dest_root = dest_tree.getroot()


def delete_node_in_xml(project_name):
    print('Deleting {}'.format(project_name))
    # find node whose name is `project_name`.
    project_node = dest_root.find("./project/[@name='{}']".format(project_name))
    if project_node is not None:
        dest_root.remove(project_node)


# Main process start

with open('invision_repo.xml') as fp:
    name_attribute_pattern = re.compile(r'<project.+name=\"(\S+)\"')
    line = fp.readline()
    while line:
        res = re.search(name_attribute_pattern, line)
        if res is not None:
            curr_project_name = res.group(1)
            delete_node_in_xml(curr_project_name)
        line = fp.readline()
    dest_tree.write('output.xml')

# Main process done

# =============================================================================
# End
# =============================================================================
__author__ = 'Willie'
__copyright__ = 'Copyright 2019, AlgorithmByPython'
__credits__ = ['Willie Xie']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'Willie'
__email__ = 'xieweikol@gmail.com'
__status__ = 'Prototype'

print('\n\n')
print('# ' + '=' * 78)
print('Author: ' + __author__)
print('Copyright: ' + __copyright__)
print('Credits: ' + ', '.join(__credits__))
print('License: ' + __license__)
print('Version: ' + __version__)
print('Maintainer: ' + __maintainer__)
print('Email: ' + __email__)
print('Status: ' + __status__)
print('# ' + '=' * 78)
