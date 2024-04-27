"""added life span field

Revision ID: d63d70f94731
Revises: 61cb577a869e
Create Date: 2024-04-27 08:49:20.983153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd63d70f94731'
down_revision = '61cb577a869e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tracker_activities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('life_span_days', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tracker_activities', schema=None) as batch_op:
        batch_op.drop_column('life_span_days')

    # ### end Alembic commands ###