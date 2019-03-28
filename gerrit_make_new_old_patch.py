#!/usr/bin/env python
#
# Author: Willie
# Version: 1.0 2019-1-15
#    Step 1: Parse manifest.xml in .repo/manifests/invision_repo.xml, to fetch all <project> note that has attribute
#            ``revision = "idealens"``. Then Store attribute ``path`` to list.
#            This is realized in function ``parse_manifest_xml()``
#    Step 2: The output new old folder is in current folder. Need to create ``out/new`` and ``out/old`` sub folders,
#            which contain all matched projects.
#            This is realized in function ``create_output_folder()``
#    Step 3: Collect different files to new and old folder.
#            This is realized in function ``make_new_old()``
#
# Sample: python3 gerrit_make_new_old_patch.py -s "2019-2-28 0:0:0" -d "/home/willie/work/idealens_version" -o "/home/willie/work/idealens_oem/amss_standard_oem" -b "idealens"
#
#
# Version: 1.1 2019-2-16 When there is no commit before the specific date in one repository, use the first commit as old commit.
# Version: 1.2 2019-3-27 If input work directory not end with "/", add it.
# Version: 1.3 2019-3-28 Add branch name option and single project name option.
#                        When fetching old and new commit-id, **MUST NOT** add ``--no-merges`` option.

import datetime
import optparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

global_options = optparse.OptionParser(
    usage="gerrit_make_new_old_patch COMMAND [ARGS]"
    , version="%prog 1.1")
global_options.add_option('-s', '--start', action='store', type='string', dest='start_time', default='',
                          help='start time, default is today 00:00')
global_options.add_option('-e', '--end', action='store', type='string', dest='end_time', default='',
                          help='end time, default is now')
global_options.add_option('-d', '--directory', action='store', type='string', dest='work_directory', default='',
                          help='repo base directory, default is current folder')
global_options.add_option('-o', '--oem', action='store', type='string', dest='oem_directory', default='',
                          help='oem directory, default is current folder')
global_options.add_option('-b', '--branch', action='store', type='string', dest='branch_name', default='',
                          help='branch name to identify <project>')
global_options.add_option('-p', '--project', action='store', type='string', dest='project_path', default='',
                          help='single project path, if empty,  is all projects')


def parse_manifest_xml(file_path, branch_name):
    """
    Parse .repo/manifests/manifest.xml, and find <project revision="idealens"> node\n
    :param file_path: xml file path
    :return: matched node 'path' attribute list, as well as <remote> node `name` attribute
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    remote_node = root.find('./remote')
    remote_name = remote_node.get('name')
    print('start parse_manifest_xml root={} <remote> name={}'.format(root, remote_name))

    path_list = []
    for project in root.findall("./project/[@revision='{}']".format(branch_name)):
        name = project.get('name')
        path = project.get('path')
        print('project_name={}, path={}'.format(name, path))
        path_list.append(path)
    return path_list, remote_name


def create_output_folder(base_folder_path, project_path_list):
    """
    Prepare folder for new and old files.\n
    :param base_folder_path: the path to create `out` folder
    :param project_path_list: all project path lists
    :return: None
    """
    print('create_output_folder start base_folder_path={}, len(project_path_list)={}'.format(base_folder_path,
                                                                                             len(project_path_list)))
    out_new_base_dir = base_folder_path + '/out/new/'
    out_old_base_dir = base_folder_path + '/out/old/'
    # delete out folder in folder firstly.
    print('delete out folder firstly')
    os.system('rm -rf {0}'.format(base_folder_path + '/out'))

    for project_path in project_path_list:
        new_project_path = out_new_base_dir + project_path
        old_project_path = out_old_base_dir + project_path
        if not os.path.exists(new_project_path):
            os.makedirs(new_project_path)
        if not os.path.exists(old_project_path):
            os.makedirs(old_project_path)

    print('create_output_folder done successfully')


def make_new_old(git_project_path, output_base_folder, relative_project_path, start_time, end_time, log_file,
                 remote_name, branch_name):
    """
    Make different files to out new and old folders.\n
    :param git_project_path: full path of git project.
    :param output_base_folder: the base output folder to place new and old files
    :param relative_project_path: the relative path of project.
    :param start_time: the lower limit of time
    :param end_time: the upper limit of time
    :param log_file: log file
    :param remote_name: git remote repository name
    :param branch_name: git branch name
    :return: None
    """

    # Firstly Splice project path and output path.
    curr_project_out_new_full_path = output_base_folder + '/out/new/' + relative_project_path
    curr_project_out_old_full_path = output_base_folder + '/out/old/' + relative_project_path
    print('\nmake_new_old start handling {}'.format(git_project_path))

    # Secondly cd project folder
    os.chdir(git_project_path)

    # Thirdly make sure current project is clean and up to date
    # Run `git stash` to clean current project.
    subprocess.run(['git', 'stash'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    # Run `git checkout -b remote_name/branch_name
    new_local_branch_name = branch_name + '_' + datetime.datetime.now().strftime('%Y%m%d__%H%M%S')
    remote_branch_name = remote_name + '/' + branch_name
    print('make new local branch to be {}; remote branch is {}'.format(new_local_branch_name, remote_branch_name))
    subprocess.run(['git', 'checkout', '-b', new_local_branch_name, remote_branch_name], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    # Fourthly fetch old commit-id and new commit-id.
    # Use ``"%H"`` to only show commit-id of log.
    # Use ``-1`` to show top 1 log.
    # If either old or new commit-id not exist, rm ``out/new`` and ``out/old`` folder and return directly.

    # Willie note here, must not add ``--no-merges`` option.
    # str_fetch_old_log_cmd = 'git log --no-merges --pretty="%ci_%H" --before="{}" -1'.format(start_time)
    str_fetch_old_log_cmd = 'git log --pretty="%ci_%H" --before="{}" -1'.format(start_time)
    old_time_commit_id = os.popen(str_fetch_old_log_cmd).read().strip()
    if (old_time_commit_id is None) or (old_time_commit_id == ""):
        # Current repository is created after old_time, so firstly try to fetch the first commit_id:
        print('old_time_commit_id is empty, try to fetch first commit')
        str_fetch_first_log_cmd = 'git log --no-merges --pretty="%ci_%H" | tail -n 1'
        old_time_commit_id = os.popen(str_fetch_first_log_cmd).read().strip()
        if (old_time_commit_id is None) or (old_time_commit_id == ""):
            # There isn't any commit in this repository, return directly
            print('There is no commit id. No need to create new old patch.')
            log_file.write('\tNo need to create new old patch.\n')
            os.system('rm -rf {0} {1}'.format(curr_project_out_new_full_path, curr_project_out_old_full_path))
            return

    # str_fetch_new_log_cmd = 'git log --no-merges --pretty="%ci_%H" --since="{}" --before="{}" -1'.format(start_time,
    #                                                                                                      end_time)
    str_fetch_new_log_cmd = 'git log --pretty="%ci_%H" --since="{}" --before="{}" -1'.format(start_time,
                                                                                             end_time)
    new_time_commit_id = os.popen(str_fetch_new_log_cmd).read().strip()
    if (new_time_commit_id is None) or (new_time_commit_id == ""):
        print('No new commit id. No need to create new old patch.')
        log_file.write('\tNo need to create new old patch.\n\n')
        os.system('rm -rf {0} {1}'.format(curr_project_out_new_full_path, curr_project_out_old_full_path))
        return

    old_split_index = old_time_commit_id.index('_')
    new_split_index = new_time_commit_id.index('_')
    old_commit_time = old_time_commit_id[:old_split_index]
    new_commit_time = new_time_commit_id[:new_split_index]
    old_commit_id = old_time_commit_id[old_split_index + 1:]
    new_commit_id = new_time_commit_id[new_split_index + 1:]

    log_file.write('\tOld CommitTime is {}\t\t CommitId is {}\n'.format(old_commit_time, old_commit_id))
    log_file.write('\tNew CommitTime is {}\t\t CommitId is {}\n'.format(new_commit_time, new_commit_id))

    # Fifthly run command to
    # willie note here 2019-1-16
    # 1. Use ``git diff`` to fetch different files between old and new.
    #    **Note:** The first parameter is old commit-id, the second is new commit-id.
    #    Use ``--diff-filter`` to filter files that are deleted.
    #    Use ``--name-only`` to only show file relative path.
    # 2. Use ``git archive`` to collect files that from the result of ``git diff`` operation.
    #    These file contents are snapshot from new commit-id .
    # 3. Decompress new files to ``out/new/`` folder
    # 4. Reverse the order of new and old to get old files folder.
    str_git_archive_new_cmd = 'git archive --format=tar {new} $(git diff --name-only --diff-filter=d {old} {new}) | (cd {out} && tar xf -)'.format(
        new=new_commit_id, old=old_commit_id, out=curr_project_out_new_full_path)
    str_git_archive_old_cmd = 'git archive --format=tar {old} $(git diff --name-only --diff-filter=d {new} {old}) | (cd {out} && tar xf -)'.format(
        new=new_commit_id, old=old_commit_id, out=curr_project_out_old_full_path)

    # Use ``os.system()`` to run these two commands above.
    print(str_git_archive_new_cmd)
    os.system(str_git_archive_new_cmd)
    print(str_git_archive_old_cmd)
    os.system(str_git_archive_old_cmd)
    print('make_new_old {} done\n'.format(project_path))
    log_file.write('\tPatch {} done successfully\n\n'.format(git_project_path))


if __name__ == '__main__':
    (options, args) = global_options.parse_args()

    # Firstly fetch parameters from input.
    start_time = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    if (options.start_time is None) or (options.start_time == ""):
        print("Input start_time is empty set start_time={}".format(start_time))
    else:
        start_time = datetime.datetime.strptime(options.start_time, '%Y-%m-%d  %H:%M:%S')
        print('set start_time={}'.format(start_time))
    str_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    end_time = datetime.datetime.now()
    if (options.end_time is None) or (options.end_time == ""):
        print('Input end_time is empty set end_time={}'.format(end_time))
    else:
        end_time = datetime.datetime.strptime(options.end_time, '%Y-%m-%d  %H:%M:%S')
        print('Set end_time={}'.format(end_time))
    str_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    repo_base_directory = os.path.dirname(os.path.realpath(__file__))
    if (options.work_directory is None) or (options.work_directory == ""):
        print('Input work_directory is empty set repo_base_directory={}'.format(repo_base_directory))
    else:
        repo_base_directory = options.work_directory
        if not repo_base_directory.endswith('/'):
            repo_base_directory = repo_base_directory + '/'
        print('Set repo_base_directory={}'.format(repo_base_directory))

    oem_git_directory = os.path.dirname(os.path.realpath(__file__))
    if (options.oem_directory is None) or (options.oem_directory == ""):
        print('Input oem_directory is empty set oem_git_directory={}'.format(oem_git_directory))
    else:
        oem_git_directory = options.oem_directory
        if not oem_git_directory.endswith('/'):
            oem_git_directory = oem_git_directory + '/'
        print('Set oem_git_directory={}'.format(oem_git_directory))

    branch_name = 'idealens'
    if (options.branch_name is None) or (options.branch_name == ""):
        print('Input branch_name is empty set branch_name={}'.format(branch_name))
    else:
        branch_name = options.branch_name
        print('Set branch_name={}'.format(branch_name))

    single_project_path = ''
    if (options.project_path is None) or (options.project_path == ""):
        print('Input project_path is empty set single_project_path={}'.format(single_project_path))
    else:
        single_project_path = options.project_path
        print('Set single_project_path={}'.format(single_project_path))

    # Secondly check exist of invision_repo_path
    invision_repo_path = repo_base_directory + '.repo/manifests/invision_repo.xml'
    print('invision_repo_path={}'.format(invision_repo_path))
    if not os.path.exists(invision_repo_path):
        print('Error {} is not valid'.format(invision_repo_path))
        sys.exit()

    # Thirdly parse manifest xml
    project_path_list, remote_name = parse_manifest_xml(invision_repo_path, branch_name)
    if (single_project_path != ''):
        project_path_list.clear()
        project_path_list.append(single_project_path)
    else:
        # Append oem folder.
        project_path_list.append('oem')

    # Fourthly prepare output folder
    curr_working_folder_path = os.path.dirname(os.path.realpath(__file__))
    out_base_folder_path = curr_working_folder_path
    create_output_folder(out_base_folder_path, project_path_list)

    # Fifthly Create log file.
    str_time_now = datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')
    str_log_file = out_base_folder_path + '/out/willie_patch_log_' + str_time_now
    log_file = open(str_log_file, 'w')
    log_file.write('Start creating patch at {}\n\n'.format(str_time_now))
    log_file.write('start_time={}\n'.format(str_start_time))
    log_file.write('end_time={}\n'.format(str_end_time))
    log_file.write('repo_base_directory={}\n'.format(repo_base_directory))
    log_file.write('oem_git_directory={}\n\n'.format(oem_git_directory))
    log_file.write('Start handling {} projects in branch idealens:\n'.format(len(project_path_list)))

    # Sixthly iterate all projects and make new/old folder.
    for idx, project_path in enumerate(project_path_list):
        log_file.write('{}: current project path is {}\n'.format(idx, project_path))
        git_project_path = repo_base_directory + project_path
        if 'oem' == project_path:
            git_project_path = oem_git_directory
        # Here change back datetime.time to string
        make_new_old(git_project_path, out_base_folder_path, project_path, str_start_time, str_end_time, log_file,
                     remote_name, branch_name)

    # Change back to original folder
    os.chdir(curr_working_folder_path)
    log_file.write('Mission complete!\n')
    log_file.close()

    # Seventhly zip out folder
    str_zip_cmd = 'zip -r new_old_{}.zip {}'.format(str_time_now, 'out')
    os.system(str_zip_cmd)
    print('\n\nMission complete!')
