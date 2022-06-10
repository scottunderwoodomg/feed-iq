"""feeds table

Revision ID: fcefcef011d4
Revises: e36adae099e7
Create Date: 2022-06-05 10:37:33.752823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcefcef011d4'
down_revision = 'e36adae099e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('feed_timestamp', sa.DateTime(), nullable=True),
    sa.Column('feed_type', sa.String(length=120), nullable=True),
    sa.Column('child_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['child_id'], ['child.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feed_feed_timestamp'), 'feed', ['feed_timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_feed_feed_timestamp'), table_name='feed')
    op.drop_table('feed')
    # ### end Alembic commands ###