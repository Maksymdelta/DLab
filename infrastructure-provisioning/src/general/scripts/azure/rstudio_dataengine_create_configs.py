#!/usr/bin/python

# *****************************************************************************
#
# Copyright (c) 2016, EPAM SYSTEMS INC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ******************************************************************************

from botocore.client import Config
from fabric.api import *
import argparse
import os
import sys
import time
from fabric.api import lcd
from fabric.contrib.files import exists
from fabvenv import virtualenv
from dlab.notebook_lib import *
from dlab.actions_lib import *
from dlab.fab import *
from dlab.common_lib import *

parser = argparse.ArgumentParser()
parser.add_argument('--cluster_name', type=str, default='')
parser.add_argument('--spark_version', type=str, default='')
parser.add_argument('--hadoop_version', type=str, default='')
parser.add_argument('--region', type=str, default='')
parser.add_argument('--os_user', type=str, default='')
parser.add_argument('--spark_master', type=str, default='')
parser.add_argument('--keyfile', type=str, default='')
parser.add_argument('--notebook_ip', type=str, default='')
args = parser.parse_args()

spark_dir = '/opt/' + args.emr_version + '/' + args.cluster_name + '/spark/'
spark_version = args.spark_version
hadoop_version = args.hadoop_version
spark_link = "http://d3kbcqa49mib13.cloudfront.net/spark-" + spark_version + "-bin-hadoop" + hadoop_version + ".tgz"


def configure_rstudio():
    if not os.path.exists('/home/' + args.os_user + '/.ensure_dir/rstudio_dataengine_ensured'):
        try:
            local('echo "export R_LIBS_USER=' + spark_dir + '/R/lib:" >> /home/' + args.os_user + '/.bashrc')
            local("sed -i 's/^SPARK_HOME/#SPARK_HOME/' /home/" + args.os_user + "/.Renviron")
            local('echo \'SPARK_HOME="' + spark_dir + '"\' >> /home/' + args.os_user + '/.Renviron')
            local("sed -i 's/^master/#master/' /home/" + args.os_user + "/.Rprofile")
            local('echo \'# Cluster - "' + args.cluster_name + '"\' >> /home/' + args.os_user + '/.Rprofile')
            local('echo \'master="' + args.spark_master + '"\' >> /home/' + args.os_user + '/.Rprofile')
            local('touch /home/' + args.os_user + '/.ensure_dir/rstudio_dataengine_ensured')
        except:
            sys.exit(1)
    else:
        try:
            local("sed -i '/R_LIBS_USER/ { s|=\(.*\)|=\\1" + spark_dir + "/R/lib:| }' /home/" + args.os_user + "/.bashrc")
            local("sed -i 's/^SPARK_HOME/#SPARK_HOME/' /home/" + args.os_user + "/.Renviron")
            local('echo \'SPARK_HOME="' + spark_dir + '"\' >> /home/' + args.os_user + '/.Renviron')
            local("sed -i 's/^master/#master/' /home/" + args.os_user + "/.Rprofile")
            local('echo \'# Cluster - "' + args.cluster_name + '"\' >> /home/' + args.os_user + '/.Rprofile')
            local('echo \'master="' + args.spark_master + '"\' >> /home/' + args.os_user + '/.Rprofile')
        except:
            sys.exit(1)


if __name__ == "__main__":
    if args.dry_run == 'true':
        parser.print_help()
    else:
        dataengine_dir_prepare('/opt/{}/'.format(args.cluster_name))
        install_dataengine_spark(spark_link, spark_version, hadoop_version, spark_dir, args.os_user)
        configure_rstudio()
