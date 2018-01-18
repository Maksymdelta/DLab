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

import logging
import json
import sys
from dlab.fab import *
from dlab.meta_lib import *
from dlab.actions_lib import *
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--uuid', type=str, default='')
args = parser.parse_args()


if __name__ == "__main__":
    instance_class = 'notebook'
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    notebook_config = dict()
    try:
        notebook_config['exploratory_name'] = os.environ['exploratory_name']
    except:
        notebook_config['exploratory_name'] = ''
    notebook_config['service_base_name'] = os.environ['conf_service_base_name']
    notebook_config['instance_type'] = os.environ['aws_notebook_instance_type']
    notebook_config['key_name'] = os.environ['conf_key_name']
    notebook_config['user_keyname'] = os.environ['edge_user_name']
    notebook_config['instance_name'] = os.environ['conf_service_base_name'] + "-" + os.environ[
        'edge_user_name'] + "-nb-" + notebook_config['exploratory_name'] + "-" + args.uuid
    notebook_config['expected_ami_name'] = os.environ['conf_service_base_name'] + '-' + os.environ['application'] + \
                                           '-notebook-image'
    notebook_config['role_profile_name'] = os.environ['conf_service_base_name'].lower().replace('-', '_') + "-" + \
                                           os.environ['edge_user_name'] + "-nb-Profile"
    notebook_config['security_group_name'] = os.environ['conf_service_base_name'] + "-" + os.environ[
        'edge_user_name'] + "-nb-SG"
    notebook_config['tag_name'] = notebook_config['service_base_name'] + '-Tag'
    notebook_config['rstudio_pass'] = id_generator()
    notebook_config['dlab_ssh_user'] = os.environ['conf_os_user']

    # generating variables regarding EDGE proxy on Notebook instance
    instance_hostname = get_instance_hostname(notebook_config['tag_name'], notebook_config['instance_name'])
    edge_instance_name = os.environ['conf_service_base_name'] + "-" + os.environ['edge_user_name'] + '-edge'
    edge_instance_hostname = get_instance_hostname(notebook_config['tag_name'], edge_instance_name)
    keyfile_name = "{}{}.pem".format(os.environ['conf_key_dir'], os.environ['conf_key_name'])

    try:
        if os.environ['conf_os_family'] == 'debian':
            initial_user = 'ubuntu'
            sudo_group = 'sudo'
        if os.environ['conf_os_family'] == 'redhat':
            initial_user = 'ec2-user'
            sudo_group = 'wheel'

        logging.info('[CREATING DLAB SSH USER]')
        print('[CREATING DLAB SSH USER]')
        params = "--hostname {} --keyfile {} --initial_user {} --os_user {} --sudo_group {}".format\
            (instance_hostname, os.environ['conf_key_dir'] + os.environ['conf_key_name'] + ".pem", initial_user,
             notebook_config['dlab_ssh_user'], sudo_group)

        try:
            local("~/scripts/{}.py {}".format('create_ssh_user', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        append_result("Failed creating ssh user 'dlab'.", str(err))
        remove_ec2(notebook_config['tag_name'], notebook_config['instance_name'])
        sys.exit(1)

    # configuring proxy on Notebook instance
    try:
        logging.info('[CONFIGURE PROXY ON R_STUDIO INSTANCE]')
        print('[CONFIGURE PROXY ON R_STUDIO INSTANCE]')
        additional_config = {"proxy_host": edge_instance_hostname, "proxy_port": "3128"}
        params = "--hostname {} --instance_name {} --keyfile {} --additional_config '{}' --os_user {}" \
            .format(instance_hostname, notebook_config['instance_name'], keyfile_name, json.dumps(additional_config),
                    notebook_config['dlab_ssh_user'])
        try:
            local("~/scripts/{}.py {}".format('common_configure_proxy', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        append_result("Failed to configure proxy.", str(err))
        remove_ec2(notebook_config['tag_name'], notebook_config['instance_name'])
        sys.exit(1)

    # updating repositories & installing python packages
    try:
        logging.info('[INSTALLING PREREQUISITES TO R_STUDIO NOTEBOOK INSTANCE]')
        print('[INSTALLING PREREQUISITES TO R_STUDIO NOTEBOOK INSTANCE]')
        params = "--hostname {} --keyfile {} --user {} --region {}".\
            format(instance_hostname, keyfile_name, notebook_config['dlab_ssh_user'], os.environ['aws_region'])
        try:
            local("~/scripts/{}.py {}".format('install_prerequisites', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        append_result("Failed installing apps: apt & pip.", str(err))
        remove_ec2(notebook_config['tag_name'], notebook_config['instance_name'])
        sys.exit(1)

    # installing and configuring R_STUDIO and all dependencies
    try:
        logging.info('[CONFIGURE R_STUDIO NOTEBOOK INSTANCE]')
        print('[CONFIGURE R_STUDIO NOTEBOOK INSTANCE]')
        params = "--hostname {}  --keyfile {} --region {} --rstudio_pass {} --rstudio_version {} --os_user {} --r_mirror {}" \
            .format(instance_hostname, keyfile_name, os.environ['aws_region'], notebook_config['rstudio_pass'],
                    os.environ['notebook_rstudio_version'], notebook_config['dlab_ssh_user'], os.environ['notebook_r_mirror'])
        try:
            local("~/scripts/{}.py {}".format('configure_rstudio_node', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        append_result("Failed to configure rstudio.", str(err))
        remove_ec2(notebook_config['tag_name'], notebook_config['instance_name'])
        sys.exit(1)

    try:
        print('[INSTALLING USERs KEY]')
        logging.info('[INSTALLING USERs KEY]')
        additional_config = {"user_keyname": notebook_config['user_keyname'],
                             "user_keydir": os.environ['conf_key_dir']}
        params = "--hostname {} --keyfile {} --additional_config '{}' --user {}".format(
            instance_hostname, keyfile_name, json.dumps(additional_config), notebook_config['dlab_ssh_user'])
        try:
            local("~/scripts/{}.py {}".format('install_user_key', params))
        except:
            traceback.print_exc()
            raise Exception
    except Exception as err:
        append_result("Failed installing users key.", str(err))
        remove_ec2(notebook_config['tag_name'], notebook_config['instance_name'])
        sys.exit(1)

    try:
        print('[SETUP USER GIT CREDENTIALS]')
        logging.info('[SETUP USER GIT CREDENTIALS]')
        params = '--os_user {} --notebook_ip {} --keyfile "{}"' \
            .format(notebook_config['dlab_ssh_user'], instance_hostname, keyfile_name)
        try:
            local("~/scripts/{}.py {}".format('manage_git_creds', params))
        except:
            append_result("Failed setup git credentials")
            raise Exception
    except Exception as err:
        append_result("Failed to setup git credentials.", str(err))
        remove_ec2(notebook_config['tag_name'], notebook_config['instance_name'])
        sys.exit(1)

    if notebook_config['shared_ami_enabled'] == 'true':
        params = "--expected_ami_name {} --tag_name {} --instance_name {}" \
            .format(notebook_config['expected_ami_name'], notebook_config['tag_name'], notebook_config['instance_name'])
        try:
            local("~/scripts/{}.py {}".format('common_create_ami', params))
        except:
            traceback.print_exc()
            raise Exception
    else:
        append_result("Image of notebook will be created by USER")

    # generating output information
    ip_address = get_instance_ip_address(notebook_config['tag_name'], notebook_config['instance_name']).get('Private')
    dns_name = get_instance_hostname(notebook_config['tag_name'], notebook_config['instance_name'])
    rstudio_ip_url = "http://" + ip_address + ":8787/"
    rstudio_dns_url = "http://" + dns_name + ":8787/"
    ungit_ip_url = "http://" + ip_address + ":8085/"
    print('[SUMMARY]')
    logging.info('[SUMMARY]')
    print("Instance name: {}".format(notebook_config['instance_name']))
    print("Private DNS: {}".format(dns_name))
    print("Private IP: {}".format(ip_address))
    print("Instance ID: {}".format(get_instance_by_name(notebook_config['tag_name'], notebook_config['instance_name'])))
    print("Instance type: {}".format(notebook_config['instance_type']))
    print("Key name: {}".format(notebook_config['key_name']))
    print("User key name: {}".format(notebook_config['user_keyname']))
    print("AMI name: {}".format(notebook_config['expected_ami_name']))
    print("Profile name: {}".format(notebook_config['role_profile_name']))
    print("SG name: {}".format(notebook_config['security_group_name']))
    print("Rstudio URL: {}".format(rstudio_ip_url))
    print("Rstudio URL: {}".format(rstudio_dns_url))
    print("Rstudio user: {}".format(notebook_config['dlab_ssh_user']))
    print("Rstudio pass: {}".format(notebook_config['rstudio_pass']))
    print("Ungit URL: {}".format(ungit_ip_url))
    print('SSH access (from Edge node, via IP address): ssh -i {0}.pem {1}@{2}'.
          format(notebook_config['key_name'], notebook_config['dlab_ssh_user'], ip_address))
    print('SSH access (from Edge node, via FQDN): ssh -i {0}.pem {1}@{2}'.
          format(notebook_config['key_name'], notebook_config['dlab_ssh_user'], dns_name))

    with open("/root/result.json", 'w') as result:
        res = {"hostname": dns_name,
               "ip": ip_address,
               "instance_id": get_instance_by_name(notebook_config['tag_name'], notebook_config['instance_name']),
               "master_keyname": os.environ['conf_key_name'],
               "notebook_name": notebook_config['instance_name'],
               "Action": "Create new notebook server",
               "exploratory_url": [
                   {"description": "RStudio",
                    "url": rstudio_ip_url},
                   {"description": "Ungit",
                    "url": ungit_ip_url}],
               "exploratory_user": notebook_config['dlab_ssh_user'],
               "exploratory_pass": notebook_config['rstudio_pass']}
        result.write(json.dumps(res))