"""added Post.status column

Revision ID: c60278daaa07
Revises: 801163fe61ad
Create Date: 2022-01-14 14:29:52.137206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c60278daaa07'
down_revision = '801163fe61ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('status', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'status')
    # ### end Alembic commands ###
