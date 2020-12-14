#!/usr/bin/env python
#
# Author: Willie
# Version: 1.0 2019-3-14
# There is a repo folder created by `repo init` and `repo sync`. Base on this folder, create mirror repo so that others
# can download this mirror repository.
#
# Note:
#    1. Use `cp -L` to copy source file instead of symbolic file
#    2. Use `del remote_node.attrib["review"]` to delete node attribute for ElementTree. It must be surrounded by
#       `try ... catch`
#    3. Use `root.find("./remote/[@name='{}']".format(ori_remote_name))` to find specific node whose node name is
#        `remote` and it has attribute named `name`, valued `ori_remote_name`
#    4. Use `subprocess.run([], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)` to hide output and error message.
#    5. If `os.makedirs()` input folder has existed, error will happen. So `if not os.path.isdir()` must be called.
#
# Sample: Create mirror repo directory "/home/willie/work/repo_android_mirror" from working directory "/home/willie/work/android/aosp"
#   python3 create_mirror_repo_from_local_folder.py -b "/home/willie/work/android/aosp" -d "/home/willie/work/repo_android_mirror"
#
# Version: 1.1 2019-3-27 Support loading <include> node
# Version: 1.2 2019-4-11
#              a. Use list instead of dictionary. So the final <project> node order in mirror manifest is the same as ori one.
#              b. If some project path do not exist, remove them from manifest.xml
# Version: 1.3 2019-4-20 Fix bug when there is <include> node in manifest.xml


import optparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

from xml.dom import minidom

global_options = optparse.OptionParser(
    usage="create_mirror_repo_from_local_folder COMMAND [ARGS]"
    , version="%prog 1.3")
global_options.add_option('-b', '--base', action='store', type='string',
                          dest='base_folder', default='',
                          help='base repo folder, default is ./base_repo')
global_options.add_option('-d', '--dest', action='store', type='string',
                          dest='dest_folder', default='',
                          help='dest mirror repo folder, default is ./mirror_repo')
global_options.add_option('-r', '--remote', action='store', type='string',
                          dest='remote_name', default='',
                          help='remote node name in manifest.xml')
global_options.add_option('-c', '--cull', action='store', type='string',
                          dest='cull_prefix', default='',
                          help='cull project name prefix in manifest.xml, default cull nothing')

global_default_git_user_name = 'willie'
global_default_git_user_email = 'xieweikol@gmail.com'


def is_empty(s):
    """
    Check input string is empty
    :param s: string to be checked
    :return: if empty, return true
    """
    return (s is None) or (s == "")


def parse_manifest_xml(out_project_path, out_project_name, repo_base_directory,
                       manifest_folder, manifest_name,
                       project_name_prefix_cull=''):
    """
    Parse .repo/manifest.xml, and find all <project> node save to path list and name list\n
    If there is <include> node, load the include manifest file\n
    :param out_project_path: output project path list
    :param out_project_name: output project name list
    :param repo_base_directory: input repo directory path
    :param manifest_folder: input path of `.repo/manifests/`
    :param manifest_name: input manifest xml name
    :param project_name_prefix_cull: <project> node `name` attribute prefix to cull
    :return: None
    """
    print(
        '\nstart parse_manifest_xml manifest_folder={}, manifest_name={}'.format(
            manifest_folder, manifest_name))
    if not manifest_folder.endswith('/'):
        manifest_folder = manifest_folder + '/'
    manifest_xml_path = manifest_folder + manifest_name
    tree = ET.parse(manifest_xml_path)
    root = tree.getroot()

    # Add all project list in <project> node, save to out_dict
    # when meet two <project> nodes with same `path` attribute, the latter one will cover the former
    for project in root.findall("./project"):
        name = project.get('name')
        # Use substring without `project_name_prefix_cull`
        name = name[len(project_name_prefix_cull):]
        path = project.get('path')
        # If there is no `path` attribute, set path=name
        if is_empty(path):
            path = name
        project_full_path = repo_base_directory + path
        if not os.path.isdir(project_full_path):
            print('Skip add project: {} for it does NOT exist'.format(
                project_full_path))
            continue

        # print('Add project name={}, path={}'.format(name, path))
        if path in out_project_path:
            # Update value in out_project_name list
            path_idx = out_project_path.index(path)
            old_name = out_project_name[path_idx]
            out_project_name[path_idx] = name
            print('Update project name={}, path={}'.format(
                out_project_name[path_idx], path))
        else:
            out_project_path.append(path)
            out_project_name.append(name)
            print('Add project name={}, path={}'.format(name, path))

    # Thirdly check include node
    for manifest in root.findall("./include"):
        include_xml_name = manifest.get('name')
        print(
            '\nAdd include manifest manifest_folder={}, include_xml_name={}'.format(
                manifest_folder, include_xml_name))
        parse_manifest_xml(out_project_path, out_project_name,
                           repo_base_directory, manifest_folder,
                           include_xml_name,
                           project_name_prefix_cull)


def handle_single_repository(base_repo_path, mirror_repo_path, project_name,
                             project_path):
    """
    create project bare repository from working folder `.git` folder
    :param base_repo_path: base repo path
    :param mirror_repo_path: destination repo path
    :param project_name: project destination relative path under mirror_repo_path
    :param project_path: project ori relative path under base_repo_path
    :return: None
    """

    full_project_path = base_repo_path + project_path
    project_git_path = full_project_path + "/.git"
    dest_project_path = mirror_repo_path + project_name + ".git"
    dest_project_parent_path = os.path.dirname(dest_project_path)
    if not os.path.isdir(dest_project_parent_path):
        os.makedirs(dest_project_parent_path)

    # Before copying `.git` folder in working repository, enter working project, and try to create new branch `master`
    # If there is no master branch, after mirror repo is created, and when others try to fetch this repo,
    # `repo sync` operation will be failed for `Couldn't find remote ref refs/heads/master`
    os.chdir(full_project_path)

    # Since `git checkout -b master` may failed for `master` branch existed, Here use `subprocess.run` hide output
    # information.
    # os.system('git checkout -b master')
    subprocess.run(['git', 'checkout', '-b', 'master'],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    # *Note* here must add `-L` option for `cp` command, so source file instead of symbolic file can be copied.
    # Use `subprocess.run` instead of `os.system` since in `subprocess.run`, I can hide output information.
    # os.system('cp -rL {} {}'.format(project_git_path, dest_project_path))
    subprocess.run(['cp', '-rL', project_git_path, dest_project_path],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    # enter dest_project_path
    os.chdir(dest_project_path)
    # make this project to be bare repository
    os.system('git config --bool core.bare true')

    print("finish processing {}\n".format(dest_project_path))


def generate_manifest(mirror_repo_path, ori_manifest_path, project_path_list,
                      project_name_list, remote_name,
                      project_name_prefix_cull):
    """
    Create New manifest.xml based on the original one.\n
    Then create working manifests git repository.\n
    Finally create bare manifests repository\n
    :param mirror_repo_path: mirror repo folder path
    :param ori_manifest_path: original repo folder manifest.xml
    :param project_path_list: project path list from ``parse_manifest_xml``
    :param project_name_list: project name list from ``parse_manifest_xml``
    :param remote_name: <remote> node name in newly created manifest.xml
    :param project_name_prefix_cull: <project> node `name` attribute prefix to cull
    :return: created bare manifests git path
    """
    manifests_work_folder_path = mirror_repo_path + ".repo/manifests"
    dest_manifest_xml_path = manifests_work_folder_path + '/default.xml'
    print(
        '\ngenerate_manifest start manifests_work_folder_path={}\ndest_manifest_xml_path={}'.format(
            manifests_work_folder_path, dest_manifest_xml_path))
    os.makedirs(manifests_work_folder_path)
    os.chdir(manifests_work_folder_path)

    # Save <project> node which has child node to dictionary
    project_with_child_dict = {}
    # Check ori tree, Find all <project> node that have child node.
    ori_tree = ET.parse(ori_manifest_path)
    ori_root = ori_tree.getroot()
    for project_node in ori_root.findall(".//project/*/.."):
        ori_name = project_node.get('name')
        ori_name = ori_name[len(project_name_prefix_cull):]
        ori_path = project_node.get('path')
        # If there is no `path` attribute, set path=name
        if (ori_path is None) or (ori_path == ""):
            ori_path = ori_name
        # Key is project path, value is project node
        project_with_child_dict[ori_path] = project_node

    # Create manifest.xml
    mirror_root = ET.Element('manifest')
    mirror_root.set('version', '1.0')
    mirror_root.append(
        ET.Comment('Generated by WilliePythonKits cr.py for mirror repo'))

    mirror_remote_node = ET.SubElement(mirror_root, 'remote')
    mirror_remote_node.set('fetch', '..')
    mirror_remote_node.set('name', remote_name)

    mirror_default_node = ET.SubElement(mirror_root, 'default')
    mirror_default_node.set('remote', remote_name)
    mirror_default_node.set('revision', 'master')

    for path, name in zip(project_path_list, project_name_list):
        if path in project_with_child_dict:
            # If current <project> path is in project_with_child_dict, use it
            project_node = project_with_child_dict[path]
            # Remove `upstream` and `revision` attributes
            try:
                del project_node.attrib['upstream']
                del project_node.attrib['revision']
            except KeyError:
                pass
            # Update `name` and `path` attributes.
            project_node.set('name', name)
            project_node.set('path', path)
            # Append node to manifest root node.
            mirror_root.append(project_node)
        else:
            mirror_project_node = ET.SubElement(mirror_root, 'project')
            mirror_project_node.set('name', name)
            mirror_project_node.set('path', path)

    # Fourthly save manifest xml
    # Willie note here 2019-3-27
    # If use ``ElementTree.write()`` to create xml, the saved file is badly formatted.
    # So here use ``xml.dom.minidom`` to transform xml to string, then save xml
    # ET.ElementTree(mirror_root).write(dest_manifest_xml_path)
    str_manifest_xml = minidom.parseString(
        ET.tostring(mirror_root)).toprettyxml(indent="   ")
    with open(dest_manifest_xml_path, "w") as f:
        f.write(str_manifest_xml)

    os.system('git init')
    os.system('git add -A')
    os.system('git commit -m "Init the manifests repository"')
    work_manifests_git_folder_path = manifests_work_folder_path + "/.git"
    bare_manifests_folder_path = mirror_repo_path + 'platform/manifests.git'
    bare_manifests_parent_folder_path = os.path.dirname(
        bare_manifests_folder_path)
    if not os.path.isdir(bare_manifests_parent_folder_path):
        os.makedirs(bare_manifests_parent_folder_path)

    subprocess.run(['cp', '-rL', work_manifests_git_folder_path,
                    bare_manifests_folder_path], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    # enter dest_project_path
    os.chdir(bare_manifests_folder_path)
    # make this project to be bare repository
    os.system('git config --bool core.bare true')

    print(
        '\ngenerate_manifest done. You can sync this mirror repo with the following command:\nrepo init -u {}\nrepo sync -c -j4\n'.format(
            bare_manifests_folder_path))
    return bare_manifests_folder_path


if __name__ == '__main__':
    # Firstly fetch parameters from input.
    print('Mission Start!\nStep 1 : fetch parameters')
    (options, args) = global_options.parse_args()

    repo_base_directory = os.path.dirname(
        os.path.realpath(__file__)) + 'base_repo/'
    if (options.base_folder is None) or (options.base_folder == ""):
        print('Input base_folder is empty set repo_base_directory={}'.format(
            repo_base_directory))
    else:
        repo_base_directory = options.base_folder
        if not repo_base_directory.endswith('/'):
            repo_base_directory = repo_base_directory + '/'
        print('Set repo_base_directory={}'.format(repo_base_directory))

    if not os.path.isdir(repo_base_directory):
        print('Error base repo folder {} is not exist'.format(
            repo_base_directory))
        sys.exit()

    repo_mirror_directory = os.path.dirname(
        os.path.realpath(__file__)) + 'mirror_repo/'
    if (options.dest_folder is None) or (options.dest_folder == ""):
        print('Input dest_folder is empty set repo_mirror_directory={}'.format(
            repo_mirror_directory))
    else:
        repo_mirror_directory = options.dest_folder
        if not repo_mirror_directory.endswith('/'):
            repo_mirror_directory = repo_mirror_directory + '/'
        print('Set repo_mirror_directory={}'.format(repo_mirror_directory))

    # delete repo_mirror_directory folder firstly.
    if os.path.isdir(repo_mirror_directory):
        print('delete mirror folder firstly')
        os.system('rm -rf {0}'.format(repo_mirror_directory))

    repo_remote_name = 'willie'
    if (options.remote_name is None) or (options.remote_name == ''):
        print('Input remote_name is empty set repo_remote_name={}'.format(
            repo_remote_name))
    else:
        repo_remote_name = options.remote_name
        print('Set repo_remote_name={}'.format(repo_remote_name))

    project_name_prefix_cull = ''
    if (options.cull_prefix is None) or (options.cull_prefix == ''):
        print(
            'Input cull_prefix is empty set project_name_prefix_cull={}'.format(
                ''))
    else:
        project_name_prefix_cull = options.cull_prefix
        if not project_name_prefix_cull.endswith('/'):
            project_name_prefix_cull = project_name_prefix_cull + '/'
        print(
            'Set project_name_prefix_cull={}'.format(project_name_prefix_cull))

    print('\nStep 2 : ensure git user.name and user.email has set')
    str_fetch_git_user_name_cmd = 'git config user.name'
    git_user_name = os.popen(str_fetch_git_user_name_cmd).read().strip()
    if (git_user_name is None) or (git_user_name == ""):
        print('set git user.name to be {}'.format(global_default_git_user_name))
        os.system('git config --global user.name {}'.format(
            global_default_git_user_name))
    str_fetch_git_user_email_cmd = 'git config user.email'
    git_user_email = os.popen(str_fetch_git_user_email_cmd).read().strip()
    if (git_user_email is None) or (git_user_email == ""):
        print(
            'set git user.email to be {}'.format(global_default_git_user_email))
        os.system('git config --global user.email {}'.format(
            global_default_git_user_email))

    # Thirdly parse manifest xml
    print(
        '\nStep 3 : parse ori repo folder .repo/manifest.xml to fetch all projects')
    # Since `.repo/manifest.xml` is symbolic link file, use `readlink -f ` command to find source path
    link_manifest_xml_path = repo_base_directory + '.repo/manifest.xml'
    fetch_source_manifest_cmd = 'readlink -f {}'.format(link_manifest_xml_path)
    source_manifest_xml_path = os.popen(
        fetch_source_manifest_cmd).read().strip()
    manifest_xml_folder = os.path.dirname(source_manifest_xml_path)
    manifest_xml_name = os.path.basename(source_manifest_xml_path)
    print(
        'Start parsing manifest folder={}, name={}'.format(manifest_xml_folder,
                                                           manifest_xml_name))

    project_path_list = []
    project_name_list = []
    parse_manifest_xml(project_path_list, project_name_list,
                       repo_base_directory, manifest_xml_folder,
                       manifest_xml_name,
                       project_name_prefix_cull)
    print(
        'There are {} projects to be created\n'.format(len(project_path_list)))

    # Fourthly generate bare repository in repo_mirror_directory
    print('\nStep 4 : create all projects bare git repository')
    index = 0
    for path, name in zip(project_path_list, project_name_list):
        print('\nStart handling No.{} project {}'.format(index, name))
        handle_single_repository(repo_base_directory, repo_mirror_directory,
                                 name, path)
        index = index + 1

    # Fifthly generate manifest bare repository
    print('\nStep 5 : generate platform/manifests.git')
    generate_manifest(repo_mirror_directory, source_manifest_xml_path,
                      project_path_list, project_name_list,
                      repo_remote_name, project_name_prefix_cull)

    print('Mission Complete!')
