# backend/storage.py
# Shared in-memory store — imported by both the router and graph nodes
# to avoid circular imports.

from typing import Dict
from backend.schemas.api import ApprovalCard

cards_db: Dict[str, ApprovalCard] = {}
