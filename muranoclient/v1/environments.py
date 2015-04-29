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

from muranoclient.common import base


class Environment(base.Resource):
    def __repr__(self):
        return "<Environment %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class Status(base.Resource):
    def __repr__(self):
        return '<Status %s>' % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class EnvironmentManager(base.ManagerWithFind):
    resource_class = Environment

    def list(self):
        return self._list('/v1/environments', 'environments')

    def create(self, data):
        return self._create('/v1/environments', data)

    def update(self, environment_id, name):
        return self._update('/v1/environments/{id}'.format(id=environment_id),
                            data={'name': name})

    def delete(self, environment_id):
        return self._delete('/v1/environments/{id}'.format(id=environment_id))

    def get(self, environment_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        return self._get("/v1/environments/{id}".format(id=environment_id),
                         headers=headers)

    def last_status(self, environment_id, session_id):
        headers = {'X-Configuration-Session': session_id}
        path = '/v1/environments/{id}/lastStatus'
        path = path.format(id=environment_id)
        status_dict = self._get(path, return_raw=True,
                                response_key='lastStatuses',
                                headers=headers)
        result = {}
        for k, v in status_dict.iteritems():
            if v:
                result[k] = Status(self, v, loaded=True)
        return result
