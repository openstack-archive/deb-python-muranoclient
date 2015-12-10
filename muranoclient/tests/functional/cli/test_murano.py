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

import unittest

from muranoclient.tests.functional.cli import \
    murano_test_utils as utils


class SimpleReadOnlyMuranoClientTest(utils.CLIUtilsTestBase):
    """Basic, read-only tests for Murano CLI client.

    Basic smoke test for the Murano CLI commands which do not require
    creating or modifying murano objects.
    """

    def test_category_list(self):
        category = self.get_table_struct('category-list')
        self.assertEqual(['ID', 'Name'], category)

    def test_env_template_list(self):
        templates = self.get_table_struct('env-template-list')
        self.assertEqual(['ID', 'Name', 'Created', 'Updated'], templates)

    def test_environment_list(self):
        environment = self.get_table_struct('environment-list')
        self.assertEqual(['ID', 'Name', 'Created', 'Updated'], environment)

    def test_package_list(self):
        packages = self.get_table_struct('package-list')
        self.assertEqual(['ID', 'Name', 'FQN', 'Author', 'Active',
                          'Is Public'], packages)


class TableStructureMuranoClientTest(utils.CLIUtilsTestBase):
    """Smoke test for the Murano CLI commands which checks table
    structure after create or delete category, env-template
    environment and package.
    """

    def test_table_struct_deployment_list(self):
        """Test scenario:
            1) create environment
            2) check table structure
        """
        environment = self.create_murano_object('environment',
                                                'MuranoTestTS-depl-list')
        table_struct = self.get_table_struct('deployment-list',
                                             params=environment['ID'])
        self.assertEqual(['ID', 'State', 'Created', 'Updated', 'Finished'],
                         table_struct)

    def test_table_struct_of_environment_create(self):
        """Test scenario:
            1) create environment
            2) check table structure
        """
        self.create_murano_object('environment', 'MuranoTestTS-env-create')
        table_struct = self.get_table_struct('environment-list')
        self.assertEqual(['ID', 'Name', 'Created', 'Updated'], table_struct)

    def test_table_struct_of_environment_delete(self):
        """Test scenario:
            1) create environment
            2) delete environment
            3) check table structure
        """
        environment = self.create_murano_object('environment',
                                                'MuranoTestTS-env-del')
        self.delete_murano_object('environment', environment)
        table_struct = self.get_table_struct('environment-list')
        self.assertEqual(['ID', 'Name', 'Created', 'Updated'], table_struct)

    def test_table_struct_of_category_create(self):
        """Test scenario:
            1) create category
            2) check table structure
        """
        self.create_murano_object('category', 'MuranoTestTS-cat-create')
        table_struct = self.get_table_struct('category-list')
        self.assertEqual(['ID', 'Name'], table_struct)

    def test_table_struct_of_category_delete(self):
        """Test scenario:
            1) create category
            2) delete category
            3) check table structure
        """
        category = self.create_murano_object('category',
                                             'MuranoTestTS-cat-create')
        self.delete_murano_object('category', category)
        category = self.get_table_struct('category-list')
        self.assertEqual(['ID', 'Name'], category)

    def test_table_struct_of_env_template_create(self):
        """Test scenario:
            1) create env_template
            2) check table structure
        """
        self.create_murano_object('env-template',
                                  'MuranoTestTS-env-tmp-create')
        table_struct = self.get_table_struct('env-template-list')
        self.assertEqual(['ID', 'Name', 'Created', 'Updated'], table_struct)

    def test_table_struct_of_env_template_delete(self):
        """Test scenario:
            1) create env_template
            2) delete env_template
            3) check table structure
        """
        env_template = self.create_murano_object('env-template',
                                                 'MuranoTestTS-env-tmp-create')
        self.delete_murano_object('env-template', env_template)
        table_struct = self.get_table_struct('env-template-list')
        self.assertEqual(['ID', 'Name', 'Created', 'Updated'], table_struct)


class EnvironmentMuranoSanityClientTest(utils.CLIUtilsTestBase):
    """Sanity tests for testing actions with environment.

    Smoke test for the Murano CLI commands which checks basic actions with
    environment command like create, delete, rename etc.
    """

    def test_environment_create(self):
        """Test scenario:
            1) create environment
            2) check that created environment exist
        """
        environment = self.create_murano_object('environment',
                                                'TestMuranoSanityEnv')
        env_list = self.listing('environment-list')

        self.assertIn(environment, env_list)

    def test_environment_delete(self):
        """Test scenario:
            1) create environment
            2) delete environment
        """
        environment = self.create_murano_object('environment',
                                                'TestMuranoSanityEnv')
        self.delete_murano_object('environment', environment)
        env_list = self.listing('environment-list')

        self.assertNotIn(environment, env_list)

    def test_environment_rename(self):
        """Test scenario:
            1) create environment
            2) rename environment
        """
        environment = self.create_murano_object('environment',
                                                'TestMuranoSanityEnv')

        new_env_name = self.generate_name('TestMuranoSEnv-env-rename')
        rename_params = "{0} {1}".format(environment['Name'], new_env_name)
        new_list = self.listing('environment-rename', params=rename_params)
        renamed_env = self.get_object(new_list, new_env_name)
        self.addCleanup(self.delete_murano_object, 'environment', renamed_env)
        new_env_list = self.listing('environment-list')

        self.assertIn(renamed_env, new_env_list)
        self.assertNotIn(environment, new_env_list)

    def test_table_struct_env_show(self):
        """Test scenario:
            1) create environment
            2) check structure of env_show object
        """
        environment = self.create_murano_object('environment',
                                                'TestMuranoSanityEnv')
        env_show = self.listing('environment-show', params=environment['Name'])
        # Check structure of env_show object
        self.assertEqual(['acquired_by', 'created', 'id', 'name', 'services',
                          'status', 'tenant_id', 'updated', 'version'],
                         map(lambda x: x['Property'], env_show))

    def test_environment_show(self):
        """Test scenario:
            1) create environment
            2) check that env_name, ID, updated and created values
               exist in env_show object
        """
        environment = self.create_murano_object('environment',
                                                'TestMuranoSanityEnv')
        env_show = self.listing('environment-show', params=environment['Name'])

        self.assertIn(environment['Created'],
                      map(lambda x: x['Value'], env_show))
        self.assertIn(environment['Updated'],
                      map(lambda x: x['Value'], env_show))
        self.assertIn(environment['Name'], map(lambda x: x['Value'], env_show))
        self.assertIn(environment['ID'], map(lambda x: x['Value'], env_show))


class CategoryMuranoSanityClientTest(utils.CLIUtilsTestBase):
    """Sanity tests for testing actions with Category.

    Smoke test for the Murano CLI commands which checks basic actions with
    category command like create, delete etc.
    """

    def test_category_create(self):
        """Test scenario:
            1) create category
            2) check that created category exist
        """
        category = self.create_murano_object('category',
                                             'TestMuranoSanityCategory')
        category_list = self.listing('category-list')

        self.assertIn(category, category_list)

    def test_category_delete(self):
        """Test scenario:
            1) create category
            2) delete category
            3) check that category has been deleted successfully
        """
        category = self.create_murano_object('category',
                                             'TestMuranoSanityCategory')
        self.delete_murano_object('category', category)
        category_list = self.listing('category-list')

        self.assertNotIn(category, category_list)

    def test_table_struct_category_show(self):
        """Test scenario:
            1) create category
            2) check table structure of category-show object
        """
        category = self.create_murano_object('category',
                                             'TestMuranoSanityCategory')
        category_show = self.listing('category-show', params=category['ID'])

        self.assertEqual(['id', 'name', 'packages'],
                         map(lambda x: x['Property'], category_show))

    def test_category_show(self):
        """Test scenario:
            1) create category
            2) check that category values exist in category_show object
        """
        category = self.create_murano_object('category',
                                             'TestMuranoSanityCategory')
        category_show = self.listing('category-show', params=category['ID'])

        self.assertIn(category['ID'], map(lambda x: x['Value'], category_show))
        self.assertIn(category['Name'],
                      map(lambda x: x['Value'], category_show))


class EnvTemplateMuranoSanityClientTest(utils.CLIUtilsTestBase):
    """Sanity tests for testing actions with Environment template.

    Smoke test for the Murano CLI commands which checks basic actions with
    env-temlate command like create, delete etc.
    """
    def test_environment_template_create(self):
        """Test scenario:
            1) create environment template
            2) check that created environment template exist
        """
        env_template = self.create_murano_object('env-template',
                                                 'TestMuranoSanityEnvTemp')
        env_template_list = self.listing('env-template-list')

        self.assertIn(env_template, env_template_list)

    def test_environment_template_delete(self):
        """Test scenario:
            1) create environment template
            2) delete environment template
            3) check that deleted environment template doesn't exist
        """
        env_template = self.create_murano_object('env-template',
                                                 'TestMuranoSanityEnvTemp')
        env_template_list = self.delete_murano_object('env-template',
                                                      env_template)

        self.assertNotIn(env_template, env_template_list)

    def test_table_struct_env_template_show(self):
        """Test scenario:
            1) create environment template
            2) check table structure of env-template-show object
        """
        env_template = self.create_murano_object('env-template',
                                                 'TestMuranoSanityEnvTemp')
        env_template_show = self.listing('env-template-show',
                                         params=env_template['ID'])
        tested_env_template = map(lambda x: x['Property'], env_template_show)

        self.assertIn('created', tested_env_template)
        self.assertIn('id', tested_env_template)
        self.assertIn('name', tested_env_template)
        self.assertIn('services', tested_env_template)
        self.assertIn('tenant_id', tested_env_template)
        self.assertIn('updated', tested_env_template)
        self.assertIn('version', tested_env_template)

    def test_env_template_show(self):
        """Test scenario:
            1) create environment template
            2) check that environment template values exist in
            env-template-show object
        """
        env_template = self.create_murano_object('env-template',
                                                 'TestMuranoSanityEnvTemp')
        env_template_show = self.listing('env-template-show',
                                         params=env_template['ID'])
        tested_env = map(lambda x: x['Value'], env_template_show)

        self.assertIn(env_template['ID'], tested_env)
        self.assertIn(env_template['Name'], tested_env)
        self.assertIn(env_template['Updated'], tested_env)
        self.assertIn(env_template['Created'], tested_env)

    def test_env_template_create_environment(self):
        """Test scenario:
            1) create environment template
            2) create environment from template
        """
        env_template = self.create_murano_object('env-template',
                                                 'TestMuranoSanityEnvTemp')
        new_env_name = self.generate_name('EnvFromTemp')
        params = "{0} {1}".format(env_template['ID'], new_env_name)
        env_created = self.listing('env-template-create-env', params=params)
        tested_env_created = map(lambda x: x['Property'], env_created)

        self.assertIn('environment_id', tested_env_created)
        self.assertIn('session_id', tested_env_created)


class PackageMuranoSanityClientTest(utils.CLIUtilsTestPackagesBase):
    """Sanity tests for testing actions with Packages.

    Smoke tests for the Murano CLI commands which check basic actions with
    packages like import, create, delete etc.
    """

    def test_package_import_by_url(self):
        """Test scenario:
            1) import package by url
            2) check that package exists
        """
        try:
            self.run_server()
            package = self.import_package(
                self.app_name,
                'http://localhost:8089/apps/{0}.zip'.format(self.app_name)
            )
        finally:
            self.stop_server()
        package_list = self.listing('package-list')

        self.assertIn(package, package_list)

    def test_package_import_by_path(self):
        """Test scenario:
            1) import package by path
            2) check that package exists
        """
        package = self.import_package(
            self.app_name,
            self.dummy_app_path
        )
        package_list = self.listing('package-list')

        self.assertIn(package, package_list)

    def test_package_is_public(self):
        """Test scenario:
            1) import package
            2) check that package is public
        """
        package = self.import_package(
            self.app_name,
            self.dummy_app_path,
            '--is-public'
        )
        self.assertEqual(package['Is Public'], 'True')

    def test_package_delete(self):
        """Test scenario:
            1) import package
            2) delete package
            3) check that package has been deleted
        """

        package = self.import_package(
            self.app_name,
            self.dummy_app_path
        )
        package_list = self.delete_murano_object('package', package)

        self.assertNotIn(package, package_list)

    def test_package_show(self):
        """Test scenario:
            1) import package
            2) check that package values exist in
            return by package-show object
        """

        package = self.import_package(
            self.app_name,
            self.dummy_app_path
        )
        package_show = self.listing('package-show', params=package['ID'])

        tested_package = map(lambda x: x['Value'], package_show)

        self.assertIn(package['ID'], tested_package)
        self.assertIn(package['Name'], tested_package)
        self.assertIn(package['FQN'], tested_package)
        self.assertIn(package['Is Public'], tested_package)

    def test_package_import_update(self):
        """Test scenario:
            1) import package
            2) import new_package using option 'u' - update
            3) check that package has been updated
        """
        package = self.import_package(
            self.app_name,
            self.dummy_app_path
        )
        upd_package = self.import_package(
            self.app_name,
            self.dummy_app_path,
            '--exists-action', 'u'
        )
        self.assertEqual(package['Name'], upd_package['Name'])
        self.assertNotEqual(package['ID'], upd_package['ID'])

    def test_package_import_skip(self):
        """Test scenario:
            1) import package using option 's' - skip for existing package
            2) try to import the same package using option 's' - skip
            3) check that package hasn't been updated
        """
        package = self.import_package(
            self.app_name,
            self.dummy_app_path,
            '--exists-action', 's'
        )
        skip_package = self.import_package(
            self.app_name,
            self.dummy_app_path,
            '--exists-action', 's'
        )
        package_list = self.listing("package-list")

        self.assertIn(package, package_list)
        self.assertEqual(package, skip_package)

    def test_package_import_abort(self):
        """Test scenario:
            1) import package
            2) import new_package using option 'a' - skip
            3) check that package hasn't been updated
        """
        package = self.import_package(
            self.app_name,
            self.dummy_app_path
        )
        package_list = self.listing('package-list')

        self.assertIn(package, package_list)

        package = self.import_package(
            self.app_name,
            self.dummy_app_path,
            '--exists-action', 'a'
        )
        package_list = self.listing('package-list')
        self.assertNotIn(package, package_list)


class DeployMuranoEnvironmentTest(utils.CLIUtilsTestPackagesBase):
    """Test for testing Murano environment deployment.

    Test for the Murano CLI commands which checks addition of app
    to the environment, session creation and deployment of
    environment.
    """

    def test_environment_deployment(self):
        """Test scenario:
            1) import package
            2) create environment
            3) create session for created environment
            4) add application to the environment
            5) send environment to deploy
            6) check that deployment was successful
        """
        self.import_package(
            self.app_name,
            self.dummy_app_path
        )

        env_id = self.create_murano_object('environment',
                                           'TestMuranoDeployEnv')['ID']
        obj_model = {
            'op': 'add',
            'path': '/-',
            'value': {
                '?': {
                    'type': 'io.murano.apps.{0}'.format(self.app_name),
                    'id': '{0}'.format(self.generate_uuid()),
                }
            }
        }
        self.deploy_environment(env_id, obj_model)
        deployments = self.listing('deployment-list', params=env_id)

        self.assertEqual('success', deployments[0]['State'])
        self.assertEqual(1, len(deployments))

    def test_add_component_to_deployed_env(self):
        """Test scenario:
            1) import package
            2) create environment
            3) create session for created environment
            4) add application to the environment
            5) send environment to deploy
            6) check that deployment was successful
            7) add application to environment
            8) deploy environment again
        """
        self.import_package(
            self.app_name,
            self.dummy_app_path
        )

        env_id = self.create_murano_object('environment',
                                           'TestMuranoDeployEnv')['ID']
        obj_model = {
            'op': 'add',
            'path': '/-',
            'value': {
                '?': {
                    'type': 'io.murano.apps.{0}'.format(self.app_name),
                    'id': '',
                }
            }
        }
        obj_model['value']['?']['id'] = self.generate_uuid()
        self.deploy_environment(env_id, obj_model)

        deployments = self.listing('deployment-list', params=env_id)
        self.assertEqual('success', deployments[0]['State'])
        self.assertEqual(1, len(deployments))

        obj_model['value']['?']['id'] = self.generate_uuid()
        self.deploy_environment(env_id, obj_model)

        deployments = self.listing('deployment-list', params=env_id)
        self.assertEqual('success', deployments[1]['State'])
        self.assertEqual(2, len(deployments))

    # TODO(akuznetsova):  need to upskip this test when
    # https://bugs.launchpad.net/python-muranoclient/+bug/1511645 is fixed
    @unittest.expectedFailure
    def test_delete_component_from_deployed_env(self):
        """Test scenario:
            1) import package
            2) create environment
            3) create session for created environment
            4) add application to the environment
            5) send environment to deploy
            6) check that deployment was successful
            7) delete application from environment
            8) deploy environment again
        """
        self.import_package(
            self.app_name,
            self.dummy_app_path
        )

        env_id = self.create_murano_object('environment',
                                           'TestMuranoDeployEnv')['ID']

        obj_model = {
            'op': 'add',
            'path': '/-',
            'value': {
                '?': {
                    'type': 'io.murano.apps.{0}'.format(self.app_name),
                    'id': '{0}'.format(self.generate_uuid()),
                }
            }
        }
        self.deploy_environment(env_id, obj_model)

        obj_model = {
            'op': 'remove',
            'path': '/0'
        }
        self.deploy_environment(env_id, obj_model)

        deployments = self.listing('deployment-list', params=env_id)
        self.assertEqual('success', deployments[1]['State'])
        self.assertEqual(2, len(deployments))
