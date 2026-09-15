"""Network_Address.xlsx ingestion.

Pipeline: reader (xlsx -> matrices) -> classify (sheet family by header
signature) -> parsers (family -> normalized records) -> plan (dedupe vs DB,
scaffold sites/VRFs/prefixes) -> execute (commit plan with savepoints).
"""

from app.services.workbook.reader import SheetMatrix, load_workbook_bytes
from app.services.workbook.classify import classify_sheet

__all__ = ["SheetMatrix", "load_workbook_bytes", "classify_sheet"]
