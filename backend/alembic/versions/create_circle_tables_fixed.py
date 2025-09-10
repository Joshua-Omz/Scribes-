"""create_circle_tables_fixed

Revision ID: create_circle_tables_fixed
Revises: 5305bb9a4276
Create Date: 2025-09-08 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'create_circle_tables_fixed'
down_revision: Union[str, Sequence[str], None] = '5305bb9a4276'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create circle and circle_members tables."""
    # Create circles table
    op.create_table(
        'circles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_private', sa.Boolean(), default=False, nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_circles_id'), 'circles', ['id'], unique=False)

    # Create circle_members table
    op.create_table(
        'circle_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('circle_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('owner', 'admin', 'member', name='member_role_types'), nullable=False, default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('invited', 'active', 'inactive', name='member_status_types'), nullable=False, default='active'),
        sa.ForeignKeyConstraint(['circle_id'], ['circles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('circle_id', 'user_id', name='unique_circle_membership')
    )
    op.create_index(op.f('ix_circle_members_id'), 'circle_members', ['id'], unique=False)


def downgrade() -> None:
    """Drop circle and circle_members tables."""
    op.drop_index(op.f('ix_circle_members_id'), table_name='circle_members')
    op.drop_table('circle_members')
    op.drop_index(op.f('ix_circles_id'), table_name='circles')
    op.drop_table('circles')
    op.execute('DROP TYPE IF EXISTS member_role_types')
    op.execute('DROP TYPE IF EXISTS member_status_types')
