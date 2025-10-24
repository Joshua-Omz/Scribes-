"""create_circle_notes_table

Revision ID: create_circle_notes_table
Revises: create_circle_tables_fixed
Create Date: 2025-09-10 20:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'create_circle_notes_table'
down_revision: Union[str, Sequence[str], None] = 'create_circle_tables_fixed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add circle_notes table."""
    op.create_table(
        'circle_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('circle_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('shared_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['circle_id'], ['circles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('circle_id', 'note_id', name='unique_circle_note')
    )
    op.create_index(op.f('ix_circle_notes_id'), 'circle_notes', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema to remove circle_notes table."""
    op.drop_index(op.f('ix_circle_notes_id'), table_name='circle_notes')
    op.drop_table('circle_notes')
