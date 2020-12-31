# WilliePythonKits
Use python to reduce some burden work

- [Repo Kits](#repokits)
- [System Kits](#systemkits)

## RepoKits

- [make_new_old_patches_in_repo](#make_new_old_patches_in_repo)
- [create_mirror_repo_from_local_folder](#create_mirror_repo_from_local_folder)

### make_new_old_patches_in_repo

#### DESCRIPTION

**Make new old patches** under [repo](https://source.android.com/source/using-repo.html) working folder.

[`make_new_old_patches_in_repo.py`](https://github.com/WillieXie/WilliePythonKits/blob/master/repo_kits/make_new_old_patches_in_repo.py) will check manifest.xml under ``.repo/manifests/`` folder and find all projects that has the specified branch.

Then iterating all matched projects and make new old patch. The output is under current ``out`` folder. And it will be compressed to zip file.

#### OPTIONS

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -s START_TIME, --start=START_TIME
                          start time, default is today 00:00
    -e END_TIME, --end=END_TIME
                          end time, default is now
    -d WORK_DIRECTORY, --directory=WORK_DIRECTORY
                          repo base directory, default is current folder
    -m MANIFEST_XML_NAME, --manifest=MANIFEST_XML_NAME
                          manifest xml in ".repo/manifests/" folder, default
                          file is "default.xml"
    -o OEM_DIRECTORY, --oem=OEM_DIRECTORY
                          oem directory, outside of repo base directory, default
                          is current folder
    -b BRANCH_NAME, --branch=BRANCH_NAME
                          branch name to identify <project>, if empty, use
                          <default> node revision
    -p PROJECT_PATH, --project=PROJECT_PATH
                          single project path, if empty, checking all projects
    -c COMMIT_ID, --commit_id=COMMIT_ID
                        Single commit id in one project


#### SAMPLE

1. Make patch for single project `/home/willie/work/aosp/frameworks/native` in branch `dev`, the manifest use `default.xml`

   ``` bash
   python3 make_new_old_patches_in_repo.py -s "2019-4-11 21:21:0" -d "/home/willie/work/aosp" -m "default.xml" -b "dev" -p "frameworks/native"
   ```

2. Make patch for single project `/home/willie/work/aosp/frameworks/native` in branch `master`. Omitting `-d` and `-m`:

   ``` bash
   python3 make_new_old_patches_in_repo.py -s "2019-4-12 11:53:0" -p "/home/willie/work/aosp/frameworks/native"
   ```

3. Make patch for all projects in folder `/home/willie/work/aosp` and oem folder `/home/willie/work/aosp_oem` whose branch is `master`:

   ``` bash
   python3 make_new_old_patches_in_repo.py -s "2019-4-11 21:21:0" -d "/home/willie/work/aosp" -o "/home/willie/work/aosp_oem" -b "master"
   ```

4. Make patch for single project `/home/willie/work/aosp/frameworks/base` for designated commit-id `d08a8210844fd9ce5308594bde5293ec48790c3e`:

   ``` bash
   python3 make_new_old_patches_in_repo.py -p /home/willie/work/aosp/frameworks/base -c d08a8210844fd9ce5308594bde5293ec48790c3e
   ```

### create_mirror_repo_from_local_folder

#### DESCRIPTION

**Create Mirror repo directory** from other working repo directory.

There exists one working repo directory. It has spent tons of time syncing from remote server(For example: AOSP).
Now I want to create mirror repo directory in local server, however **DO NOT** sync from remote server(spending tons of time again).

[`create_mirror_repo_from_local_folder.py`](https://github.com/WillieXie/WilliePythonKits/blob/master/repo_kits/create_mirror_repo_from_local_folder.py) can parse the downloaded working repo directory and create mirror repo directory.

#### OPTIONS

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -b BASE_FOLDER, --base=BASE_FOLDER
                            base repo folder, default is ./base_repo
    -d DEST_FOLDER, --dest=DEST_FOLDER
                            dest mirror repo folder, default is ./mirror_repo
    -r REMOTE_NAME, --remote=REMOTE_NAME
                            remote node name in manifest.xml
    -c CULL_PREFIX, --cull=CULL_PREFIX
                            cull project name prefix in manifest.xml, default cull
                            nothing


#### SAMPLE

1. Create mirror repo directory `/home/willie/work/repo_android_mirror` from working directory `/home/willie/work/android/aosp`:

   ``` bash
   python3 create_mirror_repo_from_local_folder.py -b "/home/willie/work/android/aosp" -d "/home/willie/work/repo_android_mirror"
   ```


## SystemKits

- [Create Gerrit projects by xml](#CreateGerritProjectsByXml)

### CreateGerritProjectsByXml

#### DESCRIPTION

[repo](https://source.android.com/source/using-repo.html) use manifests.xml to control projects.
This script can create projects on Gerrit website with ssh command after reading manifests.xml.
It can also push first commit to Gerrit website from working directory.  

#### OPTIONS

      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -a GERRIT_ACCOUNT, --account=GERRIT_ACCOUNT
                              Administrator account to operate gerrit, default is
                              gerrit_admin
      -b BASE_XML, --base=BASE_XML
                              Base manifests.xml path, default is default.xml
      -p PROJECT_PREFIX, --prefix=PROJECT_PREFIX
                              Every project prefix, default is empty
      -i INHERIT_PROJECT, --inherit=INHERIT_PROJECT
                              Privilege project to inherit from, default is All-
                              Projects
      -o PROJECT_OWNER, --owner=PROJECT_OWNER
                              Owner of every project, default is Administrators
      -d WORK_DIRECTORY, --directory=WORK_DIRECTORY
                              Repo work directory, default is empty
      -s GERRIT_SITE, --site=GERRIT_SITE
                              Gerrit site for push operation, default is empty
      -u GERRIT_USER, --user=GERRIT_USER
                              Gerrit user for push operation, default is empty


#### SAMPLE

manifest xml `default.xml` has single <project> node:

    <project path="frameworks/native" />

1. Create Gerrit project `Android/201212/frameworks/native` base on `BasePrivilege`, owner is `Administrators`:

   ``` bash
   python3 CreateGerritProjectsByXml.py -b default.xml -p Android/201212 -i BasePrivilege -o Administrators -a gerrit_admin
   ```

2. Push working directory `frameworks/native` code to Gerrit website:

   ``` bash
   python3 CreateGerritProjectsByXml.py -b default.xml -p Android/201212 -u willie -s 192.168.1.100
   ```