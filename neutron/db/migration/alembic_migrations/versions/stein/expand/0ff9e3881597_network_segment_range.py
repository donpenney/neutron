# Copyright 2018 OpenStack Foundation
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
#

from alembic import op
import sqlalchemy as sa


"""description of revision

Revision ID: 0ff9e3881597
Revises: 195176fb410d
Create Date: 2018-12-13 01:03:14.987454

"""

# revision identifiers, used by Alembic.
revision = '0ff9e3881597'
down_revision = '195176fb410d'

network_segment_range_network_type = sa.Enum(
    'vlan', 'vxlan', 'gre', 'geneve',
    name='network_segment_range_network_type')


def upgrade():
    op.create_table(
        'network_segment_ranges',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('default', sa.Boolean(), nullable=False),
        sa.Column('shared', sa.Boolean(), nullable=False),
        sa.Column('project_id', sa.String(length=255), nullable=True),
        sa.Column('network_type', network_segment_range_network_type,
                  nullable=False),
        sa.Column('physical_network', sa.String(length=64), nullable=True),
        sa.Column('minimum', sa.Integer(), nullable=True),
        sa.Column('maximum', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
