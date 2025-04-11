"""Add index

Revision ID: 4b975280303d
Revises: 74be8c1c90d0
Create Date: 2025-04-11 15:54:52.028888

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b975280303d"
down_revision: Union[str, None] = "74be8c1c90d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
