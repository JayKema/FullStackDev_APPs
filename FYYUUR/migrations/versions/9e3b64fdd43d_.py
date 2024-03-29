"""empty message

Revision ID: 9e3b64fdd43d
Revises: c76709e3609a
Create Date: 2022-06-12 22:03:40.583294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e3b64fdd43d'
down_revision = 'c76709e3609a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artist_shows')
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'artist_id')
    op.create_table('artist_shows',
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='artist_shows_artist_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['show_id'], ['Show.id'], name='artist_shows_show_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('artist_id', 'show_id', name='artist_shows_pkey')
    )
    # ### end Alembic commands ###
