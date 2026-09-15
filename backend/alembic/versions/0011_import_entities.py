"""workbook-import entities: site/ip fields + circuits/certificates/assets/services/import_batches

Revision ID: 0011_import_entities
Revises: 0010_user_roles
Create Date: 2026-09-15

Additive-only migration for the Network_Address.xlsx import pipeline:
sites gain code/number/size/active/contact fields, ip_addresses gains
imported-inventory columns + JSONB custom_fields + import provenance, and
five new tables hold the non-IPAM sheet families and import history.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_import_entities"
down_revision = "0010_user_roles"
branch_labels = None
depends_on = None

import_batch_status = postgresql.ENUM(
    "draft", "committed", "failed", name="import_batch_status", create_type=False
)
asset_kind = postgresql.ENUM(
    "hardware", "software", name="asset_kind", create_type=False
)


def upgrade() -> None:
    op.execute("CREATE TYPE import_batch_status AS ENUM ('draft','committed','failed')")
    op.execute("CREATE TYPE asset_kind AS ENUM ('hardware','software')")

    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("stored_path", sa.String(512), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column(
            "status",
            import_batch_status,
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
        sa.Column(
            "stats",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=True,
        ),
        sa.Column("actor", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("committed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_import_batches_status", "import_batches", ["status"])

    op.create_table(
        "circuits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("env", sa.String(64), nullable=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("site_number", sa.Integer(), nullable=True),
        sa.Column("site_code", sa.String(16), nullable=True),
        sa.Column("site_name", sa.String(255), nullable=True),
        sa.Column("line_type", sa.String(32), nullable=True),
        sa.Column("bezeq_circuit_id", sa.String(64), nullable=True),
        sa.Column("node", sa.String(64), nullable=True),
        sa.Column("bw_down", sa.String(32), nullable=True),
        sa.Column("bw_up", sa.String(32), nullable=True),
        sa.Column("wan_ip", postgresql.INET(), nullable=True),
        sa.Column("app_client_num", sa.String(64), nullable=True),
        sa.Column("app_client_name", sa.String(255), nullable=True),
        sa.Column("app_service_type", sa.String(255), nullable=True),
        sa.Column("contact", sa.Text(), nullable=True),
        sa.Column("status", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_circuits_site_id", "circuits", ["site_id"])
    op.create_index("ix_circuits_line_type", "circuits", ["line_type"])
    op.create_index("ix_circuits_bezeq_circuit_id", "circuits", ["bezeq_circuit_id"])
    op.create_index("ix_circuits_import_batch_id", "circuits", ["import_batch_id"])

    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(64), nullable=True),
        sa.Column("target", sa.String(255), nullable=True),
        sa.Column("server_name", sa.String(255), nullable=True),
        sa.Column("cert_name", sa.String(255), nullable=True),
        sa.Column("expires_on", sa.Date(), nullable=True),
        sa.Column("serial_raw", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_certificates_platform", "certificates", ["platform"])
    op.create_index("ix_certificates_server_name", "certificates", ["server_name"])
    op.create_index("ix_certificates_expires_on", "certificates", ["expires_on"])
    op.create_index("ix_certificates_import_batch_id", "certificates", ["import_batch_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", asset_kind, server_default=sa.text("'hardware'"), nullable=False),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("purpose", sa.String(255), nullable=True),
        sa.Column("version", sa.String(128), nullable=True),
        sa.Column("eol_on", sa.Date(), nullable=True),
        sa.Column("support_status", sa.String(128), nullable=True),
        sa.Column("serial_number", sa.String(128), nullable=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assets_kind", "assets", ["kind"])
    op.create_index("ix_assets_model", "assets", ["model"])
    op.create_index("ix_assets_serial_number", "assets", ["serial_number"])
    op.create_index("ix_assets_site_id", "assets", ["site_id"])
    op.create_index("ix_assets_import_batch_id", "assets", ["import_batch_id"])

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("beneficiary", sa.String(255), nullable=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id", ondelete="SET NULL"), nullable=True),
        sa.Column("site_code", sa.String(16), nullable=True),
        sa.Column("doc_path", sa.Text(), nullable=True),
        sa.Column("test_info", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_services_name", "services", ["name"])
    op.create_index("ix_services_site_id", "services", ["site_id"])
    op.create_index("ix_services_import_batch_id", "services", ["import_batch_id"])

    op.add_column("sites", sa.Column("code", sa.String(16), nullable=True))
    op.add_column("sites", sa.Column("site_number", sa.Integer(), nullable=True))
    op.add_column("sites", sa.Column("size", sa.String(32), nullable=True))
    op.add_column("sites", sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False))
    op.add_column("sites", sa.Column("contact", sa.Text(), nullable=True))
    op.add_column("sites", sa.Column("address", sa.Text(), nullable=True))
    op.create_index("ix_sites_code", "sites", ["code"], unique=True)
    op.create_index("ix_sites_site_number", "sites", ["site_number"])

    op.add_column("ip_addresses", sa.Column("serial_number", sa.String(128), nullable=True))
    op.add_column("ip_addresses", sa.Column("switch_name", sa.String(255), nullable=True))
    op.add_column("ip_addresses", sa.Column("switch_port", sa.String(64), nullable=True))
    op.add_column("ip_addresses", sa.Column("counter_location", sa.String(255), nullable=True))
    op.add_column("ip_addresses", sa.Column("custom_fields", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True))
    op.add_column("ip_addresses", sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_ip_addresses_import_batch_id", "ip_addresses", ["import_batch_id"])


def downgrade() -> None:
    op.drop_index("ix_ip_addresses_import_batch_id", table_name="ip_addresses")
    for col in (
        "import_batch_id", "custom_fields", "counter_location",
        "switch_port", "switch_name", "serial_number",
    ):
        op.drop_column("ip_addresses", col)

    op.drop_index("ix_sites_site_number", table_name="sites")
    op.drop_index("ix_sites_code", table_name="sites")
    for col in ("address", "contact", "is_active", "size", "site_number", "code"):
        op.drop_column("sites", col)

    op.drop_table("services")
    op.drop_table("assets")
    op.drop_table("certificates")
    op.drop_table("circuits")
    op.drop_table("import_batches")
    op.execute("DROP TYPE IF EXISTS asset_kind")
    op.execute("DROP TYPE IF EXISTS import_batch_status")
