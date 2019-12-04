#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Willie
# Created Date: 2019-11-29
# =============================================================================
"""
Create Gerrit users by reading `gerrit_user.txt`, which format is:

    chenshifan shifan.chen@ivglass.com 
    chuiguo.zeng chuiguo.zeng@ivglass.com 
"""

# =============================================================================
# Imports
# =============================================================================
import os
import re

# Match string as `InVisionWillie wei.xie@ivglass.com`
pattern = re.compile(r'(\S+)\s+(\S+)')

with open('gerrit_users.txt') as fp:
    line = fp.readline()
    while line:
        res = re.search(pattern, line)
        full_name = res.group(1)
        email = res.group(2)
        user_name = email[:email.find('@')]
        print('full_name={}; email={}; user_name={}'.format(full_name, email,
                                                            user_name))
        # Update user and password as HTTP authentication in `/etc/nginx/.htpasswd`
        # os.system('sudo htpasswd -b /etc/nginx/.htpasswd {0} 123456'.format(user_name))

        # Run gerrit command `--add-email` for current user.
        # Note that After create http password, Gerrit User will be created only after login website.
        # So add-email operation CAN'T do right after create htpasswd.
        os.system(
            'ssh gerrit_admin gerrit set-account --add-email {0} --full-name {1} {2}'.format(
                email, full_name, user_name))
        line = fp.readline()
