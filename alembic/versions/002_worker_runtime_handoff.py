"""worker runtime handoff: task results and worker metadata

Revision ID: 002
Revises: 001
Create Date: 2026-07-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("branch", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("result", postgresql.JSONB(), nullable=True))
    op.add_column(
        "workers", sa.Column("worker_metadata", postgresql.JSONB(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("workers", "worker_metadata")
    op.drop_column("tasks", "result")
    op.drop_column("tasks", "branch")
