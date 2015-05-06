#    Copyright (c) 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import shutil
import sys
import tempfile
import zipfile

from muranoclient.common import exceptions as common_exceptions
from muranoclient.common import utils
from muranoclient.openstack.common.apiclient import exceptions
from muranoclient.v1.package_creator import hot_package
from muranoclient.v1.package_creator import mpl_package


def do_environment_list(mc, args={}):
    """List the environments."""
    environments = mc.environments.list()
    field_labels = ['ID', 'Name', 'Created', 'Updated']
    fields = ['id', 'name', 'created', 'updated']
    utils.print_list(environments, fields, field_labels, sortby=0)


@utils.arg("name", metavar="<ENVIRONMENT_NAME>",
           help="Environment name")
def do_environment_create(mc, args):
    """Create an environment."""
    mc.environments.create({"name": args.name})
    do_environment_list(mc)


@utils.arg("id", metavar="<NAME or ID>",
           nargs="+", help="Id or name of environment(s) to delete")
def do_environment_delete(mc, args):
    """Delete an environment."""
    failure_count = 0
    for environment_id in args.id:
        try:
            environment = utils.find_resource(mc.environments, environment_id)
            mc.environments.delete(environment.id)
        except exceptions.NotFound:
            failure_count += 1
            print("Failed to delete '{0}'; environment not found".
                  format(environment_id))
    if failure_count == len(args.id):
        raise exceptions.CommandError("Unable to find and delete any of the "
                                      "specified environments.")
    do_environment_list(mc)


@utils.arg("id", metavar="<NAME or ID>",
           help="Environment id or name")
@utils.arg("name", metavar="<ENVIRONMENT_NAME>",
           help="Name to which the environment will be renamed")
def do_environment_rename(mc, args):
    """Rename an environment."""
    try:
        environment = utils.find_resource(mc.environments, args.id)
        mc.environments.update(environment.id, args.name)
    except exceptions.NotFound:
        raise exceptions.CommandError("Environment %s not found" % args.id)
    else:
        do_environment_list(mc)


@utils.arg("id", metavar="<NAME or ID>",
           help="Environment id or name")
def do_environment_show(mc, args):
    """Display environment details."""
    try:
        environment = utils.find_resource(mc.environments, args.id)
    except exceptions.NotFound:
        raise exceptions.CommandError("Environment %s not found" % args.id)
    else:
        formatters = {
            "id": utils.text_wrap_formatter,
            "created": utils.text_wrap_formatter,
            "name": utils.text_wrap_formatter,
            "tenant_id": utils.text_wrap_formatter,
            "services": utils.json_formatter,

        }
        utils.print_dict(environment.to_dict(), formatters=formatters)


def do_env_template_list(mc, args={}):
    """List the environments templates."""
    env_templates = mc.env_templates.list()
    field_labels = ['ID', 'Name', 'Created', 'Updated']
    fields = ['id', 'name', 'created', 'updated']
    utils.print_list(env_templates, fields, field_labels, sortby=0)


@utils.arg("name", metavar="<ENV_TEMPLATE_NAME>",
           help="Environment Template name")
def do_env_template_create(mc, args):
    """Create an environment template."""
    mc.env_templates.create({"name": args.name})
    do_env_template_list(mc)


@utils.arg("id", metavar="<ID>",
           help="Environment Template id")
def do_env_template_show(mc, args):
    """Display environment template details."""
    try:
        env_template = mc.env_templates.get(args.id)
    except exceptions.NotFound:
        raise exceptions.CommandError("Environment template %s not found"
                                      % args.id)
    else:
        formatters = {
            "id": utils.text_wrap_formatter,
            "created": utils.text_wrap_formatter,
            "name": utils.text_wrap_formatter,
            "tenant_id": utils.text_wrap_formatter,
            "services": utils.json_formatter,

        }
        utils.print_dict(env_template.to_dict(), formatters=formatters)


@utils.arg("name", metavar="<ENV_TEMPLATE_NAME>",
           help="Environment Template name")
@utils.arg('app_template_file', metavar='<FILE>',
           help='Path to the template.')
def do_env_template_add_app(mc, args):
    """Add application to the environment template."""
    with open(args.app_template_file, "r") as myfile:
        app_file = myfile.readlines()
    mc.env_templates.create_app(args.name, app_file)
    do_env_template_list(mc)


@utils.arg("id", metavar="<ENV_TEMPLATE_ID>",
           help="Environment Template ID")
@utils.arg("service_id", metavar="<ENV_TEMPLATE_APP_ID>",
           help="Application Id")
def do_env_template_del_app(mc, args):
    """Delete application to the environment template."""
    mc.env_templates.delete_app(args.name, args.service_id)
    do_env_template_list(mc)


@utils.arg("id", metavar="<ID>",
           help="Environment Template id")
@utils.arg("name", metavar="<ENV_TEMPLATE_NAME>",
           help="Environment Template name")
def do_env_template_update(mc, args):
    """Update an environment template."""
    mc.env_templates.update(args.id, args.name)
    do_env_template_list(mc)


@utils.arg("id", metavar="<ID>",
           nargs="+", help="Id of environment(s) template to delete")
def do_env_template_delete(mc, args):
    """Delete an environment template."""
    failure_count = 0
    for env_template_id in args.id:
        try:
            mc.env_templates.delete(env_template_id)
        except exceptions.NotFound:
            failure_count += 1
            mns = "Failed to delete '{0}'; environment template not found".\
                format(env_template_id)

    if failure_count == len(args.id):
        raise exceptions.CommandError(mns)
    do_env_template_list(mc)


@utils.arg("id", metavar="<ID>",
           help="Environment id for which to list deployments")
def do_deployment_list(mc, args):
    """List deployments for an environment."""
    try:
        environment = utils.find_resource(mc.environments, args.id)
        deployments = mc.deployments.list(environment.id)
    except exceptions.NotFound:
        raise exceptions.CommandError("Environment %s not found" % args.id)
    else:
        field_labels = ["ID", "State", "Created", "Updated", "Finished"]
        fields = ["id", "state", "created", "updated", "finished"]
        utils.print_list(deployments, fields, field_labels, sortby=0)


@utils.arg("--include-disabled", default=False, action="store_true")
def do_package_list(mc, args={}):
    """List available packages."""
    filter_args = {
        "include_disabled": getattr(args, 'include_disabled', False),
    }
    packages = mc.packages.filter(**filter_args)
    field_labels = ["ID", "Name", "FQN", "Author", "Is Public"]
    fields = ["id", "name", "fully_qualified_name", "author", "is_public"]
    utils.print_list(packages, fields, field_labels, sortby=0)


@utils.arg("id", metavar="<ID>",
           help="Package ID to download")
@utils.arg("filename", metavar="file", nargs="?",
           help="Filename for download (defaults to stdout)")
def do_package_download(mc, args):
    """Download a package to a filename or stdout."""

    def download_to_fh(package_id, fh):
        fh.write(mc.packages.download(package_id))

    try:
        if not args.filename:
            download_to_fh(args.id, sys.stdout)
        else:
            with open(args.filename, 'wb') as fh:
                download_to_fh(args.id, fh)
                print("Package downloaded to %s" % args.filename)
    except exceptions.NotFound:
        raise exceptions.CommandError("Package %s not found" % args.id)


@utils.arg("id", metavar="<ID>",
           help="Package ID to show")
def do_package_show(mc, args):
    """Display details for a package."""
    try:
        package = mc.packages.get(args.id)
    except exceptions.NotFound:
        raise exceptions.CommandError("Package %s not found" % args.id)
    else:
        to_display = dict(
            id=package.id,
            type=package.type,
            owner_id=package.owner_id,
            name=package.name,
            fully_qualified_name=package.fully_qualified_name,
            is_public=package.is_public,
            enabled=package.enabled,
            class_definitions=", ".join(package.class_definitions),
            categories=", ".join(package.categories),
            tags=", ".join(package.tags),
            description=package.description
        )
        formatters = {
            'class_definitions': utils.text_wrap_formatter,
            'categories': utils.text_wrap_formatter,
            'tags': utils.text_wrap_formatter,
            'description': utils.text_wrap_formatter,
        }
        utils.print_dict(to_display, formatters)


@utils.arg("id", metavar="<ID>",
           help="Package ID to delete")
def do_package_delete(mc, args):
    """Delete a package."""
    try:
        mc.packages.delete(args.id)
    except exceptions.NotFound:
        raise exceptions.CommandError("Package %s not found" % args.id)
    else:
        do_package_list(mc)


def _handle_package_exists(mc, data, package, exists_action):
    name = package.manifest['FullName']
    while True:
        print("Importing package {0}".format(name))
        try:
            return mc.packages.create(data, {name: package.file()})
        except common_exceptions.HTTPConflict:
            print("Importing package {0} failed. Package with the same"
                  " name/classes is already registered.".format(name))
            allowed_results = ['s', 'u', 'a']
            res = exists_action
            if not res:
                while True:
                    print("What do you want to do? (s)kip, (u)pdate, (a)bort")
                    res = raw_input()
                    if res in allowed_results:
                        break
            if res == 's':
                print("Skipping.")
                return
            elif res == 'a':
                print("Exiting.")
                sys.exit()
            elif res == 'u':
                pkgs = list(mc.packages.filter(fqn=name, owned=True))
                if not pkgs:
                    msg = (
                        "Got Conflict response, but couldn't find package "
                        "'{0}' in the current tenant.\nThis probably means "
                        "conflicting package is in another tenant.\n"
                        "Please delete it manually."
                    ).format(name)
                    raise exceptions.CommandError(msg)
                elif len(pkgs) > 1:
                    msg = (
                        "Got {0} packages with name '{1}'.\nI'm not trusting "
                        "myself, please delete the package manually"
                    ).format(len(pkgs), name)
                    raise exceptions.CommandError(msg)
                print("Deleting package {0}({1})".format(name, pkgs[0].id))
                mc.packages.delete(pkgs[0].id)
                continue


@utils.arg('filename', metavar='<FILE>',
           help='Url of the murano zip package, FQPN, or path to zip package')
@utils.arg('-c', '--categories', metavar='<CAT1 CAT2 CAT3>', nargs='*',
           help='Category list to attach')
@utils.arg('--is-public', action='store_true', default=False,
           help='Make package available for user from other tenants')
@utils.arg('--version', default='',
           help='Version of the package to use from repository')
@utils.arg('--exists-action', default='', choices=['a', 's', 'u'],
           help='Default action when package already exists')
def do_package_import(mc, args):
    """Import a package.
    `FILE` can be either a path to a zip file, url or a FQPN.
    `categories` could be separated by a comma
    """
    data = {"is_public": args.is_public}

    if args.categories:
        data["categories"] = args.categories

    filename = args.filename
    if os.path.isfile(filename):
        _file = filename
    else:
        print("Package file '{0}' does not exist, attempting to download"
              "".format(args.filename))
        _file = utils.to_url(
            filename,
            version=args.version,
            base_url=args.murano_repo_url,
            extension='.zip',
            path='apps/',
        )
    try:
        package = utils.Package.from_file(_file)
    except Exception as e:
        print("Failed to create package for '{0}', reason: {1}".format(
            args.filename, e))
        return
    reqs = package.requirements(base_url=args.murano_repo_url)
    for name, package in reqs.iteritems():
        image_specs = package.images()
        if image_specs:
            print("Inspecting required images")
            try:
                imgs = utils.ensure_images(
                    glance_client=mc.glance_client,
                    image_specs=image_specs,
                    base_url=args.murano_repo_url)
                for img in imgs:
                    print("Added {0}, {1} image".format(
                        img['name'], img['id']))
            except Exception as e:
                print("Error {0} occurred while installing "
                      "images for {1}".format(e, name))
        try:
            _handle_package_exists(mc, data, package, args.exists_action)
        except exceptions.CommandError:
            raise
        except Exception as e:
            print("Error {0} occurred while installing package {1}".format(
                e, name))
    do_package_list(mc)


@utils.arg('filename', metavar='<FILE>',
           help='Bundle url, bundle name, or path to the bundle file')
@utils.arg('--is-public', action='store_true', default=False,
           help='Make packages available to users from other tenants')
@utils.arg('--exists-action', default='', choices=['a', 's', 'u'],
           help='Default action when package already exists')
def do_bundle_import(mc, args):
    """Import a bundle.
    `FILE` can be either a path to a zip file, url or name from repo.
    if `FILE` is a local file does not attempt to parse requirements and
    treat Names of packages in a bundle as file names, relative to location
    of bundle file.
    """
    local_path = None
    if os.path.isfile(args.filename):
        _file = args.filename
        local_path = os.path.dirname(os.path.abspath(args.filename))
    else:
        print("Bundle file '{0}' does not exist, attempting to download"
              "".format(args.filename))
        _file = utils.to_url(
            args.filename,
            base_url=args.murano_repo_url,
            path='/bundles/',
            extension='.bundle',
        )

    try:
        bundle_file = utils.Bundle.from_file(_file)
    except Exception as e:
        print("Failed to create bundle for '{0}', reason: {1}".format(
            args.filename, e))
        return

    data = {"is_public": args.is_public}

    for package in bundle_file.packages(
            base_url=args.murano_repo_url, path=local_path):

        requirements = package.requirements(
            base_url=args.murano_repo_url,
            path=local_path,
        )
        for name, dep_package in requirements.iteritems():
            image_specs = dep_package.images()
            if image_specs:
                print("Inspecting required images")
                try:
                    imgs = utils.ensure_images(
                        glance_client=mc.glance_client,
                        image_specs=image_specs,
                        base_url=args.murano_repo_url,
                        local_path=local_path)
                    for img in imgs:
                        print("Added {0}, {1} image".format(
                            img['name'], img['id']))
                except Exception as e:
                    print("Error {0} occurred while installing "
                          "images for {1}".format(e, name))
            try:
                _handle_package_exists(
                    mc, data, dep_package, args.exists_action)
            except exceptions.CommandError:
                raise
            except Exception as e:
                print("Error {0} occurred while "
                      "installing package {1}".format(e, name))
    do_package_list(mc)


@utils.arg('id', metavar='<ID>',
           help='Environment ID to show applications from')
@utils.arg('-p', '--path', metavar='<PATH>',
           help='Level of detalization to show. '
                'Leave empty to browse all services in the environment',
           default='/')
def do_service_show(mc, args):
    if args.path == '/':
        services = mc.services.list(args.id)
    else:
        if not args.path.startswith('/'):
            args.path = '/' + args.path
            services = [mc.services.get(args.id, args.path)]

    field_labels = ['Id', 'Name', 'Type']
    fields = ['id', 'name', 'type']
    formatters = {}

    # If services is empty, first element exists and it's None
    if hasattr(services[0], '?'):
        formatters = {'id': lambda x: getattr(x, '?')['id'],
                      'type': lambda x: getattr(x, '?')['type']}

    utils.print_list(services, fields, field_labels, formatters=formatters)


@utils.arg('-t', '--template', metavar='<HEAT_TEMPLATE>',
           help='Path to the Heat template to import as '
                'an Application Definition')
@utils.arg('-c', '--classes-dir', metavar='<CLASSES_DIRECTORY>',
           help='Path to the directory containing application classes')
@utils.arg('-r', '--resources-dir', metavar='<RESOURCES_DIRECTORY>',
           help='Path to the directory containing application resources')
@utils.arg('-n', '--name', metavar='<DISPLAY_NAME>',
           help='Display name of the Application in Catalog')
@utils.arg('-f', '--full-name', metavar='<full-name>',
           help='Fully-qualified name of the Application in Catalog')
@utils.arg('-a', '--author', metavar='<AUTHOR>', help='Name of the publisher')
@utils.arg('--tags', help='List of keywords connected to the application',
           metavar='<TAG1 TAG2>', nargs='*')
@utils.arg('-d', '--description', metavar='<DESCRIPTION>',
           help='Detailed description for the Application in Catalog')
@utils.arg('-o', '--output', metavar='<PACKAGE_NAME>',
           help='The name of the output file archive to save locally')
@utils.arg('-u', '--ui', metavar='<UI_DEFINITION>',
           help='Dynamic UI form definition')
@utils.arg('--type',
           help='Package type. Possible values: Application or Library')
@utils.arg('-l', '--logo', metavar='<LOGO>', help='Path to the package logo')
def do_package_create(mc, args):
    """Create an application package."""
    if args.template and args.classes_dir:
        raise exceptions.CommandError(
            "Provide --template for a HOT-based package, OR"
            " --classes-dir for a MuranoPL-based package")
    if not args.template and not args.classes_dir:
        raise exceptions.CommandError(
            "Provide --template for a HOT-based package, OR at least"
            "--classes-dir for a MuranoPL-based package")
    directory_path = None
    try:
        if args.template:
            directory_path = hot_package.prepare_package(args)
        else:
            directory_path = mpl_package.prepare_package(args)

        archive_name = args.output or tempfile.mktemp(prefix="murano_")

        _make_archive(archive_name, directory_path)
        print("Application package is available at " +
              os.path.abspath(archive_name))
    finally:
        if directory_path:
            shutil.rmtree(directory_path)


def _make_archive(archive_name, path):
    zip_file = zipfile.ZipFile(archive_name, 'w')
    for root, dirs, files in os.walk(path):
        for f in files:
            zip_file.write(os.path.join(root, f),
                           arcname=os.path.join(os.path.relpath(root, path),
                                                f))


def do_category_list(mc, args={}):
    """List all available categories."""
    categories = mc.categories.list()
    field_labels = ["ID", "Name"]
    fields = ["id", "name"]
    utils.print_list(categories, fields, field_labels)


@utils.arg("id", metavar="<ID>",
           help="Id of a category(s) to show")
def do_category_show(mc, args):
    category = mc.categories.get(args.id)
    # field_labels = ["ID", "Name", "Packages Assigned"]
    # fields = ["id", "name", "packages"]
    to_display = dict(id=category.id,
                      name=category.name,
                      packages=', '.join(p['name'] for p in category.packages))
    formatters = {'packages': utils.text_wrap_formatter}
    utils.print_dict(to_display, formatters)


@utils.arg("name", metavar="<CATEGORY_NAME>",
           help="Category name")
def do_category_create(mc, args):
    """Create a category."""
    mc.categories.add({"name": args.name})
    do_category_list(mc)


@utils.arg("id", metavar="<ID>",
           nargs="+", help="Id of a category(s) to delete")
def do_category_delete(mc, args):
    """Delete a category."""
    failure_count = 0
    for category_id in args.id:
        try:
            mc.categories.delete(category_id)
        except exceptions.NotFound:
            failure_count += 1
            print("Failed to delete '{0}'; category not found".
                  format(category_id))
    if failure_count == len(args.id):
        raise exceptions.CommandError("Unable to find and delete any of the "
                                      "specified categories.")
    do_category_list(mc)
