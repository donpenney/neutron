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
from neutron_lib.exceptions import network_segment_range as range_exc
from neutron_lib.plugins import utils as plugin_utils
from oslo_log import log as logging
import six

from neutron.db import common_db_mixin
from neutron.objects import base as base_obj
from neutron.objects import network_segment_range as obj_network_segment_range

LOG = logging.getLogger(__name__)


class NetworkSegmentRangeDbMixin(common_db_mixin.CommonDbMixin):
    """Mixin class to add network segment range methods."""

    def _get_network_segment_range(self, context, id):
        obj = obj_network_segment_range.NetworkSegmentRange.get_object(
            context, id=id)
        if obj is None:
            raise range_exc.NetworkSegmentRangeNotFound(range_id=id)
        return obj

    def get_network_segment_range_by_id(self, context, id):
        try:
            return self._get_network_segment_range(context, id).to_dict()
        except range_exc.NetworkSegmentRangeNotFound:
            return None

    def _validate_network_segment_range_eligible(self, network_segment_range):
        range_data = (network_segment_range.get('minimum'),
                      network_segment_range.get('maximum'))
        # Currently, network segment range only supports VLAN, VxLAN,
        # GRE and Geneve.
        if network_segment_range.get('network_type') == constants.TYPE_VLAN:
            plugin_utils.verify_vlan_range(range_data)
        else:
            plugin_utils.verify_tunnel_range(
                range_data, network_segment_range.get('network_type'))

    def create_network_segment_range(self, context, network_segment_range):
        range_data = network_segment_range['network_segment_range']
        self._validate_network_segment_range_eligible(range_data)
        network_segment_range = obj_network_segment_range.NetworkSegmentRange(
            context, name=range_data['name'], default=False,
            shared=range_data['shared'],
            project_id=(range_data['project_id']
                        if not range_data['shared'] else None),
            network_type=range_data['network_type'],
            physical_network=(range_data['physical_network']
                              if range_data['network_type'] ==
                              constants.TYPE_VLAN else None),
            minimum=range_data['minimum'],
            maximum=range_data['maximum']
        )
        network_segment_range.create()
        return network_segment_range.to_dict()

    def update_network_segment_range(self, context, id, network_segment_range):
        updated_range_data = network_segment_range['network_segment_range']

        network_segment_range = self._get_network_segment_range(
            context, id)
        old_data = network_segment_range.to_dict()
        new_data = self._add_unchanged_range_attributes(
            updated_range_data, old_data)
        self._validate_network_segment_range_eligible(new_data)
        network_segment_range.update_fields(new_data)
        network_segment_range.update()
        return network_segment_range.to_dict()

    def delete_network_segment_range(self, context, id):
        network_segment_range = self._get_network_segment_range(context, id)
        network_segment_range.delete()

    def get_network_segment_range(self, context, id, fields=None):
        network_segment_range = self._get_network_segment_range(
            context, id)
        return network_segment_range.to_dict()

    def get_network_segment_ranges(self, context, filters=None, fields=None,
                                   sorts=None, limit=None, marker=None,
                                   page_reverse=False):
        pager = base_obj.Pager(sorts, limit, page_reverse, marker)
        filters = filters or {}
        network_segment_ranges = (
            obj_network_segment_range.NetworkSegmentRange.get_objects(
                context, _pager=pager, **filters))

        return [
            network_segment_range.to_dict()
            for network_segment_range in network_segment_ranges
        ]

    def _add_unchanged_range_attributes(self, updates, existing):
        """Adds data for unspecified fields on incoming update requests."""
        for key, value in six.iteritems(existing):
            updates.setdefault(key, value)
        return updates
