
from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "tool_inventory",
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("total_qty", sa.Integer(), nullable=False),
        sa.CheckConstraint("total_qty >= 0", name="ck_total_qty_nonneg"),
    )

    op.create_table(
        "rental_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "rental_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("rental_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("start_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_ts", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("qty > 0", name="ck_qty_pos"),
        sa.CheckConstraint("end_ts > start_ts", name="ck_end_after_start"),
        sa.UniqueConstraint("order_id", "tool_id", "start_ts", "end_ts", name="uq_line_dedup"),
    )


def downgrade():
    op.drop_table("rental_lines")
    op.drop_table("rental_orders")
    op.drop_table("tool_inventory")
    op.drop_table("tools")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
