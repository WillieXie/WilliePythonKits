#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2019-12-3
# =============================================================================
"""
Read repo manifest.xml to fetch all projects.
Base on different input command, Do either:
1. create these projects on gerrit site.
2. create first commit and push to gerrit site basing on local working directory

For example, manifest xml `default.xml` has single <project> node:

    <project path="frameworks/native" />

If command is:

    python3 CreateGerritProjectsByXml.py -b default.xml -p Android/201212 -i BasePrivilege -o Administrators -a gerrit_admin

This command is equal to:

    ssh gerrit_admin gerrit create-project Android/201212/frameworks/native --parent BasePrivilege --owner Administrators;

It will create gerrit project `Android/201212/frameworks/native` base on `BasePrivilege`, owner is `Administrators`

Else if command is:

    python3 CreateGerritProjectsByXml.py -b default.xml -p Android/201212 -u willie -s 192.168.1.100

It will:

   1. read current folder manifest file named `default.xml`.
   2. parse `default.xml` and extract target `frameworks/native`.
   3. enter  subdirectory `frameworks/native`.
   4. add gerrit project url as remote server.
   5. push current HEAD node to gerrit master branch.

Version: 1.1 2020-12-14 Add option parse for creating gerrit project or
                        push commit to gerrit.

"""

# =============================================================================
# Imports
# =============================================================================
import optparse
import os
import re
import subprocess


def is_empty(s):
    """
    Check input string is empty
    :param s: string to be checked
    :return: if empty, return true
    """
    return (s is None) or (s == "")


def create_gerrit_project(_gerrit_admin_ssh, _gerrit_project_path,
                          _privilege_project, _owner):
    """
    Use gerrit command to create project with relative path

    :param _gerrit_admin_ssh: administrator to operate gerrit by ssh
    :param _gerrit_project_path: single project path
    :param _privilege_project: privilege project to inherit from
    :param _owner: owner of single project
    :return: None
    """
    print('Creating project={}'.format(_gerrit_project_path))
    os.system(
        'ssh {0} gerrit create-project {1} '
        '--parent {2} '
        '--owner {3}'.format(_gerrit_admin_ssh, _gerrit_project_path,
                             _privilege_project, _owner))


def push_first_commit(_base_dir, _project_relative_path, _user, _ip,
                      _gerrit_project_prefix):
    """
    Push first commit for project to gerrit in repo working directory

    :param _base_dir: repo working directory path
    :param _project_relative_path: every project relative path
    :param _user: gerrit user
    :param _ip: gerrit site address
    :param _gerrit_project_prefix: project prefix on gerrit site
    :return:
    """

    gerrit_url = 'ssh://' + _user + '@' + _ip + ':29418/' + \
                 _gerrit_project_prefix + _project_relative_path
    curr_project_folder = _base_dir + _project_relative_path
    print(
        'current folder is {}\ngerrit url is {}'.format(
            curr_project_folder,
            gerrit_url))

    # Step 0: check if project folder exist.
    if not os.path.isdir(curr_project_folder):
        print('\n***Error: path {} not exist\n'.format(curr_project_folder))
        return

    # Step 1: enter git working folder
    os.chdir(curr_project_folder)

    # Step 2: add gerrit url as remote
    subprocess.run(['git', 'remote', 'add', 'gerrit', gerrit_url],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    # Step 3: push directly to gerrit server
    subprocess.run(['git', 'push', '-u', 'gerrit', 'HEAD:master'],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    print('processing done')


# Main process start

global_options = optparse.OptionParser(
    usage="Create gerrit projects by gerrit ssh command COMMAND [ARGS]"
    , version="%prog 1.1")
global_options.add_option('-a', '--account', action='store', type='string',
                          dest='gerrit_account', default='gerrit_admin',
                          help='Administrator account to operate gerrit'
                               ', default is gerrit_admin')
global_options.add_option('-b', '--base', action='store', type='string',
                          dest='base_xml', default='default.xml',
                          help='Base manifests.xml path'
                               ', default is default.xml')
global_options.add_option('-p', '--prefix', action='store', type='string',
                          dest='project_prefix', default='',
                          help='Every project prefix, default is empty')
global_options.add_option('-i', '--inherit', action='store', type='string',
                          dest='inherit_project', default='All-Projects',
                          help='Privilege project to inherit from'
                               ', default is All-Projects')
global_options.add_option('-o', '--owner', action='store', type='string',
                          dest='project_owner', default='Administrators',
                          help='Owner of every project'
                               ', default is Administrators')
global_options.add_option('-d', '--directory', action='store', type='string',
                          dest='work_directory', default='',
                          help='Repo work directory, default is empty')
global_options.add_option('-s', '--site', action='store', type='string',
                          dest='gerrit_site', default='',
                          help='Gerrit site for push operation, '
                               'default is empty')
global_options.add_option('-u', '--user', action='store', type='string',
                          dest='gerrit_user', default='',
                          help='Gerrit user for push operation, '
                               'default is empty')

if __name__ == '__main__':

    (options, args) = global_options.parse_args()

    print('Mission Start!\nStep 1 : fetch parameters')
    manifests_xml_path = options.base_xml
    if not os.path.isfile(manifests_xml_path):
        print('Error base manifest xml {} is not exist'.format(
            manifests_xml_path))
        sys.exit()
    gerrit_account = options.gerrit_account
    gerrit_project_prefix = options.project_prefix
    if not is_empty(
            gerrit_project_prefix) and not gerrit_project_prefix.endswith('/'):
        gerrit_project_prefix = gerrit_project_prefix + '/'
    gerrit_privilege_project = options.inherit_project
    gerrit_project_owner = options.project_owner

    repo_working_dir = options.work_directory
    if is_empty(repo_working_dir):
        repo_working_dir = os.path.dirname(os.path.realpath(__file__))
    if not repo_working_dir.endswith('/'):
        repo_working_dir = repo_working_dir + '/'
    gerrit_site_ip = options.gerrit_site
    gerrit_site_user = options.gerrit_user
    is_create_project_operation = is_empty(gerrit_site_ip) or is_empty(
        gerrit_site_user)

    print('Fetch parameters done:\nmanifests_xml_path={}\ngerrit_account={}\n'
          'gerrit_project_prefix={}\ngerrit_privilege_project={}\n'
          'gerrit_project_owner={}\nrepo_working_dir={}\n'
          'gerrit_site_ip={}\ngerrit_site_user={}\n'
          'is_create_project_operation={}\n'.format(manifests_xml_path,
                                                    gerrit_account,
                                                    gerrit_project_prefix,
                                                    gerrit_privilege_project,
                                                    gerrit_project_owner,
                                                    repo_working_dir,
                                                    gerrit_site_ip,
                                                    gerrit_site_user,
                                                    is_create_project_operation
                                                    ))

    with open(manifests_xml_path) as fp:
        path_attribute_pattern = re.compile(r'<project.+path=\"(\S+)\"')
        line = fp.readline()
        while line:
            res = re.search(path_attribute_pattern, line)
            if res is not None:
                project_path = res.group(1)
                print('\nproject_path={}'.format(project_path))
                if is_create_project_operation:
                    create_gerrit_project(gerrit_account,
                                          gerrit_project_prefix + project_path,
                                          gerrit_privilege_project,
                                          gerrit_project_owner)
                else:
                    push_first_commit(repo_working_dir, project_path,
                                      gerrit_site_user, gerrit_site_ip,
                                      gerrit_project_prefix)
            line = fp.readline()

    os.chdir(repo_working_dir)
# Main process done


# =============================================================================
# End
# =============================================================================
__author__ = 'Willie'
__copyright__ = 'Copyright 2020, WilliePythonKits'
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
