"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2023-04-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2 as ga


# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create buses table
    op.create_table('buses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('bus_type', sa.Integer(), nullable=True),
        sa.Column('base_kv', sa.Float(), nullable=True),
        sa.Column('geometry', ga.Geography('POINT', srid=4326), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_buses_id'), 'buses', ['id'], unique=False)
    op.create_index(op.f('ix_buses_name'), 'buses', ['name'], unique=False)
    
    # Create branches table
    op.create_table('branches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('from_bus_id', sa.Integer(), nullable=True),
        sa.Column('to_bus_id', sa.Integer(), nullable=True),
        sa.Column('rate1', sa.Float(), nullable=True),
        sa.Column('rate2', sa.Float(), nullable=True),
        sa.Column('rate3', sa.Float(), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=True),
        sa.Column('geometry', ga.Geography('LINESTRING', srid=4326), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['from_bus_id'], ['buses.id'], ),
        sa.ForeignKeyConstraint(['to_bus_id'], ['buses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_branches_id'), 'branches', ['id'], unique=False)
    op.create_index(op.f('ix_branches_name'), 'branches', ['name'], unique=False)
    
    # Create generators table
    op.create_table('generators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('bus_id', sa.Integer(), nullable=True),
        sa.Column('p_gen', sa.Float(), nullable=True),
        sa.Column('q_gen', sa.Float(), nullable=True),
        sa.Column('p_max', sa.Float(), nullable=True),
        sa.Column('p_min', sa.Float(), nullable=True),
        sa.Column('q_max', sa.Float(), nullable=True),
        sa.Column('q_min', sa.Float(), nullable=True),
        sa.Column('gen_type', sa.String(), nullable=True),
        sa.Column('geometry', ga.Geography('POINT', srid=4326), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generators_id'), 'generators', ['id'], unique=False)
    op.create_index(op.f('ix_generators_name'), 'generators', ['name'], unique=False)
    
    # Create loads table
    op.create_table('loads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('bus_id', sa.Integer(), nullable=True),
        sa.Column('p_load', sa.Float(), nullable=True),
        sa.Column('q_load', sa.Float(), nullable=True),
        sa.Column('geometry', ga.Geography('POINT', srid=4326), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loads_id'), 'loads', ['id'], unique=False)
    op.create_index(op.f('ix_loads_name'), 'loads', ['name'], unique=False)
    
    # Create substations table
    op.create_table('substations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('voltage', sa.Float(), nullable=True),
        sa.Column('geometry', ga.Geography('POINT', srid=4326), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_substations_id'), 'substations', ['id'], unique=False)
    op.create_index(op.f('ix_substations_name'), 'substations', ['name'], unique=False)
    
    # Create balancing_authorities table
    op.create_table('balancing_authorities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('abbreviation', sa.String(), nullable=True),
        sa.Column('geometry', ga.Geography('POLYGON', srid=4326), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_balancing_authorities_abbreviation'), 'balancing_authorities', ['abbreviation'], unique=False)
    op.create_index(op.f('ix_balancing_authorities_id'), 'balancing_authorities', ['id'], unique=False)
    op.create_index(op.f('ix_balancing_authorities_name'), 'balancing_authorities', ['name'], unique=False)
    
    # Create weather_data table
    op.create_table('weather_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('geometry', ga.Geography('POINT', srid=4326), nullable=True),
        sa.Column('max_temperature', sa.Float(), nullable=True),
        sa.Column('avg_temperature', sa.Float(), nullable=True),
        sa.Column('min_temperature', sa.Float(), nullable=True),
        sa.Column('relative_humidity', sa.Float(), nullable=True),
        sa.Column('specific_humidity', sa.Float(), nullable=True),
        sa.Column('longwave_radiation', sa.Float(), nullable=True),
        sa.Column('shortwave_radiation', sa.Float(), nullable=True),
        sa.Column('precipitation', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weather_data_date'), 'weather_data', ['date'], unique=False)
    op.create_index(op.f('ix_weather_data_id'), 'weather_data', ['id'], unique=False)
    op.create_index(op.f('ix_weather_data_latitude'), 'weather_data', ['latitude'], unique=False)
    op.create_index(op.f('ix_weather_data_longitude'), 'weather_data', ['longitude'], unique=False)
    
    # Create heatmap_data table
    op.create_table('heatmap_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('parameter', sa.String(), nullable=True),
        sa.Column('data_json', sa.JSON(), nullable=True),
        sa.Column('bounds_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heatmap_data_date'), 'heatmap_data', ['date'], unique=False)
    op.create_index(op.f('ix_heatmap_data_id'), 'heatmap_data', ['id'], unique=False)
    op.create_index(op.f('ix_heatmap_data_parameter'), 'heatmap_data', ['parameter'], unique=False)
    
    # Create energy_emergency_alerts table
    op.create_table('energy_emergency_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ba_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ba_id'], ['balancing_authorities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_energy_emergency_alerts_date'), 'energy_emergency_alerts', ['date'], unique=False)
    op.create_index(op.f('ix_energy_emergency_alerts_id'), 'energy_emergency_alerts', ['id'], unique=False)


def downgrade():
    # Drop all tables in reverse order
    op.drop_table('energy_emergency_alerts')
    op.drop_table('heatmap_data')
    op.drop_table('weather_data')
    op.drop_table('balancing_authorities')
    op.drop_table('substations')
    op.drop_table('loads')
    op.drop_table('generators')
    op.drop_table('branches')
    op.drop_table('buses')
    op.drop_table('users')
