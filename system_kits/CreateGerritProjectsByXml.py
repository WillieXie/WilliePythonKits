#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2019-12-3
# =============================================================================
"""
Read `invision_repo.xml` in same folder, do the following two jobs:
1. Create Gerrit project by reading invision_repo.xml <project> node
   `path` attributes:

       <project path="frameworks/native" />

   Then use gerrit command to create project.

2. Enter local repo working folder, push all commits to gerrit.


"""

# =============================================================================
# Imports
# =============================================================================
import os
import re
import subprocess


def create_gerrit_project(project_relative_path):
    """
    Use gerrit command to create project with relative path

    :param project_relative_path:
    :return: None
    """
    print('Creating project={}'.format(project_relative_path))
    # project parent privilege project is `SCFrameworksAppsPrivilege`
    # project owner is Administrators
    os.system(
        'ssh gerrit_admin gerrit create-project SC/QC835/81/{0} '
        '--parent SCFrameworksAppsPrivilege '
        '--owner Administrators'.format(project_relative_path))


def commit_and_push_command(project_relative_path):
    """
    Enter every project working folder, and push directly to gerrit

    :param project_relative_path:
    :return: None
    """

    project_path_prefix = '/home/willie/tmp/test_835_repo/'
    project_local_path = project_path_prefix + project_relative_path
    gerrit_url_prefix = 'ssh://wei.xie@192.168.2.100:29418/SC/QC835/81/'
    gerrit_url = gerrit_url_prefix + project_relative_path
    print('current folder is {}. gerrit url is {}'.format(project_local_path,
                                                          gerrit_url))

    # Step 1: enter git working folder
    os.chdir(project_local_path)

    # Step 2: add gerrit url as remote
    subprocess.run(['git', 'remote', 'add', 'gerrit', gerrit_url],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    # Step 3: push directly to gerrit server
    subprocess.run(['git', 'push', 'gerrit', 'HEAD:master'],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    print('processing done')


# Main process start

with open('invision_repo.xml') as fp:
    path_attribute_pattern = re.compile(r'<project.+path=\"(\S+)\"')
    line = fp.readline()
    while line:
        res = re.search(path_attribute_pattern, line)
        if res is not None:
            project_path = res.group(1)
            print('project_path={}'.format(project_path))
            # Job 1
            # create_gerrit_project(project_path)
            # Job 2
            # commit_and_push_command(project_path)
        line = fp.readline()

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
