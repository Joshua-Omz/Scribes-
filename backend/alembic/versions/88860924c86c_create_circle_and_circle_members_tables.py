"""create circle and circle_members tables

Revision ID: 88860924c86c
Revises: f258aa22f7d9
Create Date: 2025-09-08 21:35:58.114282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88860924c86c'
down_revision: Union[str, Sequence[str], None] = 'f258aa22f7d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
