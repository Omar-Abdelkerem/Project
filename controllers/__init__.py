# controllers/__init__.py

from .application_controller import application_bp
from .admin_controller import admin_bp
from .UserController import user_controller

__all__ = ['application_bp', 'admin_bp', 'user_controller']