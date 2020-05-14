"""2020_05_14-22_13_09

Revision ID: d908c00a5181
Revises: 77f76102f99c
Create Date: 2020-05-14 20:13:11.733316

"""

# revision identifiers, used by Alembic.
revision = 'd908c00a5181'
down_revision = '77f76102f99c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mod', sa.Column('lock_reason', sa.Unicode(length=1024), nullable=True))
    op.add_column('mod', sa.Column('locked', sa.Boolean(), nullable=True))
    op.drop_column('mod', 'approved')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mod', sa.Column('approved', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('mod', 'locked')
    op.drop_column('mod', 'lock_reason')
    # ### end Alembic commands ###
