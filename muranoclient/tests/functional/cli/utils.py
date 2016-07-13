# Copyright (c) 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import zipfile

import yaml


MANIFEST = {'Format': 'MuranoPL/1.0',
            'Type': 'Application',
            'Description': 'MockApp for CLI tests',
            'Author': 'Mirantis, Inc'}


def compose_package(app_name, manifest, package_dir,
                    require=None, archive_dir=None):
    """Composes a murano package

    Composes package `app_name` with `manifest` file as a template for the
    manifest and files from `package_dir`.
    Includes `require` section if any in the manifest file.
    Puts the resulting .zip file into `archive_dir` if present or in the
    `package_dir`.
    """
    with open(manifest, 'w') as f:
        fqn = 'io.murano.apps.' + app_name
        mfest_copy = MANIFEST.copy()
        mfest_copy['FullName'] = fqn
        mfest_copy['Name'] = app_name
        mfest_copy['Classes'] = {fqn: 'mock_muranopl.yaml'}
        if require:
            mfest_copy['Require'] = require
        f.write(yaml.dump(mfest_copy, default_flow_style=False))

    name = app_name + '.zip'

    if not archive_dir:
        archive_dir = os.path.dirname(os.path.abspath(__file__))
    archive_path = os.path.join(archive_dir, name)

    with zipfile.ZipFile(archive_path, 'w') as zip_file:
        for root, dirs, files in os.walk(package_dir):
            for f in files:
                zip_file.write(
                    os.path.join(root, f),
                    arcname=os.path.join(os.path.relpath(root, package_dir), f)
                )

    return archive_path
