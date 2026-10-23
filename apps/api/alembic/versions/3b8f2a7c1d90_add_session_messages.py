"""Add session_messages for conversation restore

Revision ID: 3b8f2a7c1d90
Revises: 17ef59a741f0
Create Date: 2026-10-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3b8f2a7c1d90'
down_revision: Union[str, Sequence[str], None] = '17ef59a741f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('session_messages',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('session_id', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('payload', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['learning_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_messages_session_id'), 'session_messages', ['session_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_session_messages_session_id'), table_name='session_messages')
    op.drop_table('session_messages')
