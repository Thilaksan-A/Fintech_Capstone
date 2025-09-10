"""Modify primary constraint for reddit model

Revision ID: 38a4a1dc8963
Revises: cf49dc4e08f3
Create Date: 2025-08-02 14:22:30.092200

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '38a4a1dc8963'
down_revision = 'cb1fb464822e'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('crypto_reddit_data', schema=None) as batch_op:
        batch_op.drop_constraint('crypto_reddit_data_pkey', type_='primary')
        batch_op.create_primary_key(
            'crypto_reddit_data_pkey',
            ['symbol', 'subreddit', 'text']
        )

    # ### end Alembic commands ###


def downgrade():
    
    with op.batch_alter_table('crypto_reddit_data', schema=None) as batch_op:
        batch_op.drop_constraint('crypto_reddit_data_pkey', type_='primary')
        batch_op.create_primary_key(
            'crypto_reddit_data_pkey',
            ['symbol', 'subreddit', 'text', 'timestamp']
        )
    
    # ### end Alembic commands ###
