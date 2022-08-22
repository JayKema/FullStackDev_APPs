"""empty message

Revision ID: eb43099f6363
Revises: beb09a56af01
Create Date: 2022-06-12 19:39:34.928237

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb43099f6363'
down_revision = 'beb09a56af01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venue_shows',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('show_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['show_id'], ['Show.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('venue_id', 'show_id')
    )
    op.drop_constraint('Show_venue_id_fkey', 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('Show_venue_id_fkey', 'Show', 'Venue', ['venue_id'], ['id'])
    op.drop_table('venue_shows')
    # ### end Alembic commands ###
