"""Initial migration

Revision ID: cd8034960766
Revises: 0ce250524ea4
Create Date: 2024-07-07 22:38:17.750809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd8034960766'
down_revision: Union[str, None] = '0ce250524ea4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('domain',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.Column('scraped_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('domain')
    # ### end Alembic commands ###
