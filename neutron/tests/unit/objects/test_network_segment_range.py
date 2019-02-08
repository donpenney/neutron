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

import mock

from neutron.objects import network_segment_range
from neutron.tests.unit.objects import test_base as obj_test_base
from neutron.tests.unit import testlib_api

TEST_TENANT_ID = '46f70361-ba71-4bd0-9769-3573fd227c4b'
TEST_PHYSICAL_NETWORK = 'phys_net'


class NetworkSegmentRangeIfaceObjectTestCase(
      obj_test_base.BaseObjectIfaceTestCase):

    _test_class = network_segment_range.NetworkSegmentRange

    def setUp(self):
        self._mock_get_available_allocation = mock.patch.object(
            network_segment_range.NetworkSegmentRange,
            '_get_available_allocation',
            return_value=[])
        self.mock_get_available_allocation = (
            self._mock_get_available_allocation.start())
        self._mock_get_used_allocation_mapping = mock.patch.object(
            network_segment_range.NetworkSegmentRange,
            '_get_used_allocation_mapping',
            return_value={})
        self.mock_get_used_allocation_mapping = (
            self._mock_get_used_allocation_mapping.start())
        super(NetworkSegmentRangeIfaceObjectTestCase, self).setUp()
        # `project_id` and `physical_network` attributes in
        # network_segment_range are nullable, depending on the value of
        # `shared` and `network_type` respectively.
        # Hack to always populate test project_id and physical_network
        # fields in network segment range Iface object testing so that related
        # tests like `test_extra_fields`, `test_create_updates_from_db_object`,
        # `test_update_updates_from_db_object` can have those fields.
        # Alternatives can be skipping those tests when executing
        # NetworkSegmentRangeIfaceObjectTestCase, or making base test case
        # adjustments.
        self.update_obj_fields({'project_id': TEST_TENANT_ID,
                                'physical_network': TEST_PHYSICAL_NETWORK})


class NetworkSegmentRangeDbObjectTestCase(obj_test_base.BaseDbObjectTestCase,
                                          testlib_api.SqlTestCase):

    _test_class = network_segment_range.NetworkSegmentRange
