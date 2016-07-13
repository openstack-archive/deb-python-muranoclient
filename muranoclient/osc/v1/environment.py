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

"""Application-catalog v1 stack action implementation"""

import uuid

from cliff import lister
from cliff import show
from muranoclient.common import utils as murano_utils
from muranoclient.openstack.common.apiclient import exceptions
from openstackclient.common import utils
from oslo_log import log as logging
from oslo_serialization import jsonutils

LOG = logging.getLogger(__name__)


class ListEnvironments(lister.Lister):
    """Lists environments"""

    def get_parser(self, prog_name):
        parser = super(ListEnvironments, self).get_parser(prog_name)
        parser.add_argument(
            '--all-tenants',
            action='store_true',
            default=False,
            help='List environments from all tenants (admin only).',
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog
        data = client.environments.list(parsed_args.all_tenants)

        columns = ('id', 'name', 'status', 'created', 'updated')
        column_headers = [c.capitalize() for c in columns]
        return (
            column_headers,
            list(utils.get_item_properties(
                s,
                columns,
            ) for s in data)
        )


class ShowEnvironment(show.ShowOne):
    """Display environment details"""

    def get_parser(self, prog_name):
        parser = super(ShowEnvironment, self).get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<NAME or ID>",
            help=("Name or ID of the environment to display"),
        )
        parser.add_argument(
            "--only-apps",
            action='store_true',
            default=False,
            help="Only print apps of the environment (useful for automation).",
        )
        parser.add_argument(
            "--session-id",
            metavar="<SESSION_ID>",
            default='',
            help="Id of a config session.",
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog

        environment = utils.find_resource(client.environments,
                                          parsed_args.id)
        data = client.environments.get(environment.id,
                                       parsed_args.session_id).to_dict()

        data['services'] = jsonutils.dumps(data['services'], indent=2)

        if getattr(parsed_args, 'only_apps', False):
            return(['services'], [data['services']])
        else:
            return self.dict2columns(data)


class RenameEnvironment(lister.Lister):
    """Rename an environment."""

    def get_parser(self, prog_name):
        parser = super(RenameEnvironment, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            metavar="<NAME or ID>",
            help="Environment ID or name.",
        )
        parser.add_argument(
            'name',
            metavar="<ENVIRONMENT_NAME>",
            help="A name to which the environment will be renamed.",
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog
        environment = utils.find_resource(client.environments,
                                          parsed_args.id)
        data = client.environments.update(environment.id,
                                          parsed_args.name)

        columns = ('id', 'name', 'status', 'created', 'updated')
        column_headers = [c.capitalize() for c in columns]

        return (
            column_headers,
            [utils.get_item_properties(
                data,
                columns,
            )]
        )


class EnvironmentSessionCreate(show.ShowOne):
    """Creates a new configuration session for environment ID."""

    def get_parser(self, prog_name):
        parser = super(EnvironmentSessionCreate, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            metavar="<ID>",
            help="ID of Environment to add session to.",
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog

        environment_id = parsed_args.id
        session_id = client.sessions.configure(environment_id).id
        sessionid = murano_utils.text_wrap_formatter(session_id)

        return (['id'], [sessionid])


class EnvironmentCreate(lister.Lister):
    """Create an environment."""

    def get_parser(self, prog_name):
        parser = super(EnvironmentCreate, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar="<ENVIRONMENT_ID>",
            help="Environment name.",
        )
        parser.add_argument(
            '--region',
            metavar="<REGION_NAME>",
            help="Name of the target OpenStack region.",
        )
        parser.add_argument(
            '--join-subnet-id',
            metavar="<SUBNET_ID>",
            help="Subnetwork id to join.",
        )
        parser.add_argument(
            '--join-net-id',
            metavar="<NET_ID>",
            help="Network id to join.",
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog

        body = {"name": parsed_args.name, "region": parsed_args.region}
        if parsed_args.join_net_id or parsed_args.join_subnet_id:
            res = {
                'defaultNetworks': {
                    'environment': {
                        '?': {
                            'id': uuid.uuid4().hex,
                            'type':
                            'io.murano.resources.ExistingNeutronNetwork'
                        },
                    },
                    'flat': None
                }
            }
            if parsed_args.join_net_id:
                res['defaultNetworks']['environment']['internalNetworkName'] \
                    = parsed_args.join_net_id
            if parsed_args.join_subnet_id:
                res['defaultNetworks']['environment']['internalSubnetworkName'
                                                      ] = \
                    parsed_args.join_subnet_id

            body.update(res)

        data = client.environments.create(body)

        columns = ('id', 'name', 'status', 'created', 'updated')
        column_headers = [c.capitalize() for c in columns]

        return (
            column_headers,
            [utils.get_item_properties(
                data,
                columns,
            )]
        )


class EnvironmentDelete(lister.Lister):
    """Delete an environment."""

    def get_parser(self, prog_name):
        parser = super(EnvironmentDelete, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            metavar="<NAME or ID>",
            nargs="+",
            help="Id or name of environment(s) to delete.",
        )
        parser.add_argument(
            '--abandon',
            action='store_true',
            default=False,
            help="If set will abandon environment without deleting any of its"
                 " resources.",
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog

        abandon = getattr(parsed_args, 'abandon', False)
        failure_count = 0
        for environment_id in parsed_args.id:
            try:
                environment = murano_utils.find_resource(client.environments,
                                                         environment_id)
                client.environments.delete(environment.id, abandon)
            except exceptions.NotFound:
                failure_count += 1
                print("Failed to delete '{0}'; environment not found".
                      format(environment_id))

        if failure_count == len(parsed_args.id):
            raise exceptions.CommandError("Unable to find and delete any of "
                                          "the specified environments.")

        data = client.environments.list()

        columns = ('id', 'name', 'status', 'created', 'updated')
        column_headers = [c.capitalize() for c in columns]

        return (
            column_headers,
            list(utils.get_item_properties(
                s,
                columns,
            ) for s in data)
        )


class EnvironmentDeploy(show.ShowOne):
    """Start deployment of a murano environment session."""

    def get_parser(self, prog_name):
        parser = super(EnvironmentDeploy, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            metavar="<ENVIRONMENT_ID>",
            help="ID of Environment to deploy.",
        )
        parser.add_argument(
            '--session-id',
            metavar="<SESSION>",
            help="ID of configuration session to deploy.",
        )

        return parser

    def take_action(self, parsed_args):
        LOG.debug("take_action({0})".format(parsed_args))
        client = self.app.client_manager.application_catalog

        client.sessions.deploy(parsed_args.id, parsed_args.session_id)

        environment = utils.find_resource(client.environments,
                                          parsed_args.id)
        data = client.environments.get(environment.id,
                                       parsed_args.session_id).to_dict()

        data['services'] = jsonutils.dumps(data['services'], indent=2)

        if getattr(parsed_args, 'only_apps', False):
            return(['services'], [data['services']])
        else:
            return self.dict2columns(data)
