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

from neutron_lib.api.definitions import network_segment_range as range_def
from neutron_lib import constants as const
from neutron_lib.db import api as db_api
from neutron_lib.exceptions import network_segment_range as range_exc
from neutron_lib.plugins import directory
from oslo_config import cfg
from oslo_log import log

from neutron.extensions import network_segment_range as ext_range
from neutron.services.network_segment_range import db as range_db

LOG = log.getLogger(__name__)


def is_network_segment_range_enabled():
    network_segment_range_class = ('neutron.services.network_segment_range.'
                                   'plugin.NetworkSegmentRangePlugin')
    return any(p in cfg.CONF.service_plugins
               for p in ['network_segment_range', network_segment_range_class])


class NetworkSegmentRangePlugin(range_db.NetworkSegmentRangeDbMixin,
                                ext_range.NetworkSegmentRangePluginBase):
    """Implements Neutron Network Segment Range Service plugin."""

    supported_extension_aliases = [range_def.ALIAS]

    __native_pagination_support = True
    __native_sorting_support = True
    __filter_validation_support = True

    def __init__(self):
        super(NetworkSegmentRangePlugin, self).__init__()
        self.type_manager = directory.get_plugin().type_manager
        self.type_manager.initialize_network_segment_range_support()

    def _is_network_segment_range_referenced(self, context,
                                             network_segment_range):
        return self.type_manager.network_segments_exist(
            context, network_segment_range['network_type'],
            network_segment_range.get('physical_network'),
            network_segment_range)

    def _is_network_segment_range_type_supported(self, network_type):
        if not self.type_manager.network_type_supported(network_type) or (
                network_type not in const.NETWORK_SEGMENT_RANGE_TYPES):
            raise range_exc.NetworkSegmentRangeNetTypeNotSupported(
                type=network_type)

        return True

    def _is_existing_network_segment_range_impacted(self, context,
                                                    existing_range,
                                                    updated_range):
        updated_range_min = updated_range.get('minimum',
                                              existing_range['minimum'])
        updated_range_max = updated_range.get('maximum',
                                              existing_range['maximum'])
        existing_range_min, existing_range_max = (
            self.type_manager.network_segment_existing_range(
                context, existing_range['network_type'],
                existing_range.get('physical_network'), existing_range))

        if existing_range_min and existing_range_max:
            return bool(updated_range_min >= existing_range_min or
                        updated_range_max <= existing_range_max)
        else:
            return False

    def _update_network_segment_range_allocations(self, network_segment_range):
        network_type = network_segment_range['network_type']
        self.type_manager.update_network_segment_range_allocations(
            network_type)

    def update_network_segment_range(self, context, id, network_segment_range):
        """Check existing network segment range impact on range updates."""
        with db_api.autonested_transaction(context.session):
            existing_range = self.get_network_segment_range_by_id(context, id)

            if existing_range['default']:
                raise range_exc.NetworkSegmentRangeDefaultReadOnly(range_id=id)

            if self._is_existing_network_segment_range_impacted(
                    context, existing_range,
                    updated_range=network_segment_range[
                        'network_segment_range']):
                raise range_exc.NetworkSegmentRangeReferencedByProject(
                    range_id=id)

            network_segment_range = (
                super(NetworkSegmentRangePlugin, self).
                update_network_segment_range(
                    context, id, network_segment_range))

        self._update_network_segment_range_allocations(network_segment_range)
        return network_segment_range

    def create_network_segment_range(self, context, network_segment_range):
        """Check network types supported on network segment range creation."""
        if self._is_network_segment_range_type_supported(
                network_segment_range
                ['network_segment_range']['network_type']):
            with db_api.autonested_transaction(context.session):
                network_segment_range = (
                    super(NetworkSegmentRangePlugin, self).
                    create_network_segment_range(
                        context, network_segment_range))

        self._update_network_segment_range_allocations(network_segment_range)
        return network_segment_range

    def delete_network_segment_range(self, context, id):
        """Check segment reference on network segment range deletion."""
        with db_api.autonested_transaction(context.session):
            network_segment_range = self.get_network_segment_range_by_id(
                context, id)

            if network_segment_range['default']:
                raise range_exc.NetworkSegmentRangeDefaultReadOnly(range_id=id)

            if self._is_network_segment_range_referenced(
                    context, network_segment_range):
                raise range_exc.NetworkSegmentRangeReferencedByProject(
                    range_id=id)

            super(NetworkSegmentRangePlugin, self).\
                delete_network_segment_range(context, id)

        self._update_network_segment_range_allocations(network_segment_range)
