"""Create users table."""
from alembic import op
import sqlalchemy as sa

revision = "0001_users"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("users",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("email",sa.String(255),nullable=False),
        sa.Column("hashed_password",sa.String(255),nullable=False),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("is_superuser",sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint("email",name="uq_users_email"))
    op.create_index("ix_users_email","users",["email"])

def downgrade() -> None:
    op.drop_index("ix_users_email",table_name="users")
    op.drop_table("users")
