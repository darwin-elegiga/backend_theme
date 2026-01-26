"""
Admin module for managing brand themes.
Provides REST API and HTML panel for editing colors, uploading images, and managing fonts.
"""

from app.admin.routes import router as admin_router

__all__ = ["admin_router"]
