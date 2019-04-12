# WilliePythonKits
Use python to reduce some burden work

- [Repo Kits](#repokits)

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
