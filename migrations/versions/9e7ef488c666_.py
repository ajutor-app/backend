"""empty message

Revision ID: 9e7ef488c666
Revises: 
Create Date: 2021-06-23 16:37:00.286729

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '9e7ef488c666'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('skills',
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('skill_name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('skill_id'),
    sa.UniqueConstraint('skill_name'),
    sa.UniqueConstraint('skill_name')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=250), nullable=False),
    sa.Column('password', sa.String(length=250), nullable=False),
    sa.Column('phone', sa.String(length=100), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.Column('avatar', sa.String(length=250), nullable=True),
    sa.Column('title', sa.String(length=250), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('twoFALoggedin', sa.Boolean(), nullable=True),
    sa.Column('twoFAKey', sa.String(length=250), nullable=False),
    sa.Column('invite_code', sa.String(length=250), nullable=True),
    sa.Column('email_code', sa.String(length=250), nullable=True),
    sa.Column('sms_code', sa.String(length=250), nullable=True),
    sa.Column('apiKey', sa.String(length=255), nullable=True),
    sa.Column('emailConfirmed', sa.Boolean(), nullable=False),
    sa.Column('lastLogin', sa.String(length=30), nullable=True),
    sa.Column('userIP', sa.String(length=30), nullable=True),
    sa.Column('language_app', sa.String(length=30), nullable=True),
    sa.Column('tz', sa.String(length=50), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_disabled', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('is_phone_valid', sa.Boolean(), nullable=True),
    sa.Column('user_type', sa.Enum('client', 'expert'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('email')
    )
    op.create_table('requests',
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('files', sa.Text(), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('payment_type', sa.String(length=255), nullable=False),
    sa.Column('request_type', sa.String(length=255), nullable=False),
    sa.Column('is_approved', sa.Boolean(), nullable=False),
    sa.Column('not_approved', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('are_files_checked', sa.Boolean(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('request_id')
    )
    op.create_table('security_keys',
    sa.Column('security_key_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('credential_id', sa.String(length=250), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('pub_key', sa.String(length=65), nullable=True),
    sa.Column('sign_count', sa.Integer(), nullable=True),
    sa.Column('is_disabled', sa.Boolean(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('security_key_id'),
    sa.UniqueConstraint('credential_id'),
    sa.UniqueConstraint('credential_id'),
    sa.UniqueConstraint('pub_key'),
    sa.UniqueConstraint('pub_key')
    )
    op.create_table('request_bids',
    sa.Column('request_bid_id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('delivery_time', sa.Interval(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['request_id'], ['requests.request_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('request_bid_id')
    )
    op.create_table('request_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=True),
    sa.Column('attachment_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['request_id'], ['requests.request_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('request_skill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['request_id'], ['requests.request_id'], ),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.skill_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('request_skill')
    op.drop_table('request_files')
    op.drop_table('request_bids')
    op.drop_table('security_keys')
    op.drop_table('requests')
    op.drop_table('users')
    op.drop_table('skills')
    # ### end Alembic commands ###
