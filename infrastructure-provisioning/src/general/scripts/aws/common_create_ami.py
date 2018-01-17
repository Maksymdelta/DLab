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
from dlab.actions_lib import create_image_from_instance
from dlab.meta_lib import get_ami_id_by_name
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--expected_ami_name', type=str, default='')
parser.add_argument('--tag_name', type=str, default='')
parser.add_argument('--instance_name', type=str, default='')
args = parser.parse_args()

if __name__ == "__main__":
    try:
        print('[CREATING AMI]')
        logging.info('[CREATING AMI]')
        ami_id = get_ami_id_by_name(args.expected_ami_name)
        if ami_id == '':
            print("Looks like it's first time we configure notebook server. Creating image.")
            image_id = create_image_from_instance(tag_name=args.tag_name,
                                                  instance_name=args.instance_name,
                                                  image_name=args.expected_ami_name)
            if image_id != '':
                print("Image was successfully created. It's ID is {}".format(image_id))
    except Exception as err:
        append_result("Failed creating image.", str(err))
        remove_ec2(args.tag_name, args.instance_name)
        sys.exit(1)