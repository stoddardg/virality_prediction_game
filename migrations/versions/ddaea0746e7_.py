"""empty message

Revision ID: ddaea0746e7
Revises: 18ed8ba1aaa4
Create Date: 2016-01-10 13:54:24.677124

"""

# revision identifiers, used by Alembic.
revision = 'ddaea0746e7'
down_revision = '18ed8ba1aaa4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey_result', sa.Column('subreddit', sa.String(), nullable=True))
    op.add_column('survey_result', sa.Column('use_subreddit', sa.String(), nullable=True))
    op.drop_column('survey_result', 'type_of_use')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey_result', sa.Column('type_of_use', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('survey_result', 'use_subreddit')
    op.drop_column('survey_result', 'subreddit')
    ### end Alembic commands ###