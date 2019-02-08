# Copyright (c) 2018 Intel Corporation.
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

from neutron_lib import constants
from neutron_lib.db import constants as db_const
from neutron_lib.db import model_base
import sqlalchemy as sa


class NetworkSegmentRange(model_base.BASEV2, model_base.HasId,
                          model_base.HasProject):
    """Represents network segment range data."""
    __tablename__ = 'network_segment_ranges'

    # user-defined network segment range name
    name = sa.Column(sa.String(db_const.NAME_FIELD_SIZE), nullable=True)

    # defines whether the network segment range is loaded from host config
    # files and used as the default range when there is no other available
    default = sa.Column(sa.Boolean, default=False, nullable=False)

    # defines whether multiple tenants can use this network segment range
    shared = sa.Column(sa.Boolean, default=True, nullable=False)

    # the project_id is the subject that the policy will affect. this may
    # also be a wildcard '*' to indicate all tenants or it may be a role if
    # neutron gets better integration with keystone
    project_id = sa.Column(sa.String(db_const.PROJECT_ID_FIELD_SIZE),
                           nullable=True)

    # network segment range network type
    network_type = sa.Column(sa.Enum(constants.TYPE_VLAN,
                             constants.TYPE_VXLAN,
                             constants.TYPE_GRE,
                             constants.TYPE_GENEVE,
                             name='network_segment_range_network_type'),
                             nullable=False)

    # network segment range physical network, only applicable for VLAN.
    physical_network = sa.Column(sa.String(64))

    # minimum segmentation id value
    minimum = sa.Column(sa.Integer)

    # maximum segmentation id value
    maximum = sa.Column(sa.Integer)

    def __init__(self, id=None, name=None, default=None,
                 shared=None, project_id=None, network_type=None,
                 physical_network=None, minimum=None, maximum=None):
        self.id = id
        self.name = name
        self.default = default
        self.shared = shared
        if not self.shared:
            self.project_id = project_id
        else:
            self.project_id = None
        self.network_type = network_type
        if self.network_type == constants.TYPE_VLAN:
            self.physical_network = physical_network
        else:
            self.physical_network = None
        self.minimum = minimum
        self.maximum = maximum

    def __repr__(self):
        return "<NetworkSegmentRange(%s,%s,%s,%s,%s,%s - %s,%s)>" % (
            self.id, self.name, str(self.shared), self.project_id,
            self.network_type, self.physical_network, self.minimum,
            self.maximum)
