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
# Sample: python3 create_mirror_repo_from_local_folder.py -b "/home/git/3glass/sxr1130-la-1-0_amss_standard_oem/LINUX/android" -d "/home/git/repositories/3glass_mirror" -c "sxr1130-la10-3box"
#
#

import optparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

global_options = optparse.OptionParser(
    usage="create_mirror_repo_from_local_folder COMMAND [ARGS]"
    , version="%prog 1.0")
global_options.add_option('-b', '--base', action='store', type='string', dest='base_folder', default='',
                          help='base repo folder, default is ./base_repo')
global_options.add_option('-d', '--dest', action='store', type='string', dest='dest_folder', default='',
                          help='dest mirror repo folder, default is ./mirror_repo')
global_options.add_option('-r', '--remote', action='store', type='string', dest='remote_name', default='',
                          help='remote node name in manifest.xml')
global_options.add_option('-c', '--cull', action='store', type='string', dest='cull_prefix', default='',
                          help='cull project name prefix in manifest.xml, default cull nothing')

global_default_git_user_name = 'willie'
global_default_git_user_email = 'xieweikol@gmail.com'


def parse_manifest_xml(manifest_xml_path, project_name_prefix_cull=''):
    """
    Parse .repo/manifest.xml, and find all <project> node\n
    :param manifest_xml_path: xml file path
    :param project_name_prefix_cull: used to remove project_name prefix
    :return: 'name' attribute list and 'path' attribute list
    """
    tree = ET.parse(manifest_xml_path)
    root = tree.getroot()
    print('\nstart parse_manifest_xml root={}'.format(root))
    project_name_list = []
    path_list = []
    for project in root.findall("./project"):
        name = project.get('name')
        name = name[len(project_name_prefix_cull):]
        path = project.get('path')
        print('project_name={}, path={}'.format(name, path))
        project_name_list.append(name)
        path_list.append(path)
    return project_name_list, path_list


def handle_single_repository(base_repo_path, mirror_repo_path, project_name, project_path):
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
    subprocess.run(['git', 'checkout', '-b', 'master'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    # *Note* here must add `-L` option for `cp` command, so source file instead of symbolic file can be copied.
    # Use `subprocess.run` instead of `os.system` since in `subprocess.run`, I can hide output information.
    # os.system('cp -rL {} {}'.format(project_git_path, dest_project_path))
    subprocess.run(['cp', '-rL', project_git_path, dest_project_path], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    # enter dest_project_path
    os.chdir(dest_project_path)
    # make this project to be bare repository
    os.system('git config --bool core.bare true')

    print("finish processing {}\n".format(dest_project_path))


def generate_manifest(mirror_repo_path, ori_manifest_path, remote_name, project_prefix_cull=''):
    """
    Create manifest.xml based on current one. Then create working manifests git repository.
    Finally create bare
    :param mirror_repo_path: Destination mirror repo folder path.
    :param ori_manifest_path: Original manifest.xml path (This is a symbolic file)
    :param remote_name: default remote node name
    :param project_prefix_cull: the prefix to be cut for every `project` node `name` attribute
    :return: bare manifest path
    """
    manifests_work_folder_path = mirror_repo_path + ".repo/manifests"
    dest_manifest_xml_path = manifests_work_folder_path + '/default.xml'
    print('\ngenerate_manifest start manifests_work_folder_path={}\ndest_manifest_xml_path={}'.format(
        manifests_work_folder_path, dest_manifest_xml_path))
    os.makedirs(manifests_work_folder_path)
    os.chdir(manifests_work_folder_path)

    # Since ori_manifest_path is a symbolic file, here need to add `-L` option for `cp` command.
    os.system('cp -L {} {}'.format(ori_manifest_path, dest_manifest_xml_path))

    tree = ET.parse(dest_manifest_xml_path)
    root = tree.getroot()

    # Firstly modify <remote> and <default> node.
    default_node = root.find('default')
    ori_remote_name = default_node.get('remote')
    # Find correspond <remote> node whose name is `ori_remote_name`
    remote_node = root.find("./remote/[@name='{}']".format(ori_remote_name))
    # set remote node `fetch` attribute to be `..`. Since this manifests git will be under `platform` folder
    # Just as AOSP
    remote_node.set('fetch', '..')
    remote_node.set('name', remote_name)

    # Try to delete <remote> node `review` attribute
    try:
        del remote_node.attrib["review"]
    except KeyError:
        pass

    default_node.set('remote', remote_name)

    # Secondly Iterate every <project> node and cull `name` attribute.
    for project in root.iter("project"):
        ori_name = project.get('name')
        project.set('name', ori_name[len(project_name_prefix_cull):])

    tree.write(dest_manifest_xml_path)

    os.system('git init')
    os.system('git add -A')
    os.system('git commit -m "Init the manifests repository"')
    work_manifests_git_folder_path = manifests_work_folder_path + "/.git"
    bare_manifests_folder_path = mirror_repo_path + 'platform/manifests.git'
    bare_manifests_parent_folder_path = os.path.dirname(bare_manifests_folder_path)
    if not os.path.isdir(bare_manifests_parent_folder_path):
        os.makedirs(bare_manifests_parent_folder_path)

    subprocess.run(['cp', '-rL', work_manifests_git_folder_path, bare_manifests_folder_path], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    # enter dest_project_path
    os.chdir(bare_manifests_folder_path)
    # make this project to be bare repository
    os.system('git config --bool core.bare true')

    print('\ngenerate_manifest done bare_manifests_folder_path={}'.format(bare_manifests_folder_path))
    return bare_manifests_folder_path


if __name__ == '__main__':
    # Firstly fetch parameters from input.
    print('Mission Start!\nStep 1 : fetch parameters')
    (options, args) = global_options.parse_args()

    repo_base_directory = os.path.dirname(os.path.realpath(__file__)) + 'base_repo'
    if (options.base_folder is None) or (options.base_folder == ""):
        print('Input base_folder is empty set repo_base_directory={}'.format(repo_base_directory))
    else:
        repo_base_directory = options.base_folder
        if not repo_base_directory.endswith('/'):
            repo_base_directory = repo_base_directory + '/'
        print('Set repo_base_directory={}'.format(repo_base_directory))

    if not os.path.isdir(repo_base_directory):
        print('Error base repo folder {} is not exist'.format(repo_base_directory))
        sys.exit()

    repo_mirror_directory = os.path.dirname(os.path.realpath(__file__)) + 'mirror_repo'
    if (options.dest_folder is None) or (options.dest_folder == ""):
        print('Input dest_folder is empty set repo_mirror_directory={}'.format(repo_mirror_directory))
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
        print('Input remote_name is empty set repo_remote_name={}'.format(repo_remote_name))
    else:
        repo_remote_name = options.remote_name
        print('Set repo_remote_name={}'.format(repo_remote_name))

    project_name_prefix_cull = ''
    if (options.cull_prefix is None) or (options.cull_prefix == ''):
        print('Input cull_prefix is empty set project_name_prefix_cull={}'.format(''))
    else:
        project_name_prefix_cull = options.cull_prefix
        if not project_name_prefix_cull.endswith('/'):
            project_name_prefix_cull = project_name_prefix_cull + '/'
        print('Set project_name_prefix_cull={}'.format(project_name_prefix_cull))

    print('\nStep 2 : ensure git user.name and user.email has set')
    str_fetch_git_user_name_cmd = 'git config user.name'
    git_user_name = os.popen(str_fetch_git_user_name_cmd).read().strip()
    if (git_user_name is None) or (git_user_name == ""):
        print('set git user.name to be {}'.format(global_default_git_user_name))
        os.system('git config --global user.name {}'.format(global_default_git_user_name))
    str_fetch_git_user_email_cmd = 'git config user.email'
    git_user_email = os.popen(str_fetch_git_user_email_cmd).read().strip()
    if (git_user_email is None) or (git_user_email == ""):
        print('set git user.email to be {}'.format(global_default_git_user_email))
        os.system('git config --global user.email {}'.format(global_default_git_user_email))

    # Thirdly parse manifest xml
    print('\nStep 3 : parse ori repo folder .repo/manifest.xml to fetch all projects')
    manifest_xml_path = repo_base_directory + '.repo/manifest.xml'
    project_name_list, project_path_list = parse_manifest_xml(manifest_xml_path, project_name_prefix_cull)
    print('There are {} projects to be created\n'.format(len(project_name_list)))

    # Fourthly generate bare repository in repo_mirror_directory
    print('\nStep 4 : create all projects bare git repository')
    index = 0
    for name, path in zip(project_name_list, project_path_list):
        print('\nStart handling No.{} project {}'.format(index, name))
        handle_single_repository(repo_base_directory, repo_mirror_directory, name, path)
        index = index + 1

    # Fifthly generate manifest bare repository
    print('\nStep 5 : generate platform/manifests.git')
    generate_manifest(repo_mirror_directory, manifest_xml_path, repo_remote_name, project_name_prefix_cull)

    print('Mission Complete!')
