"""Initial migration

Revision ID: d78fc6e47be4
Revises: 5b3c3b0c0c05
Create Date: 2024-07-09 14:04:50.796141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd78fc6e47be4'
down_revision: Union[str, None] = '5b3c3b0c0c05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
