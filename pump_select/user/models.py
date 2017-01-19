# -*- coding: utf-8 -*-
"""User models."""
from flask_login import UserMixin

from pump_select.database import Column, Model, SurrogatePK, db, reference_col, relationship, Timestamps
from pump_select.extensions import bcrypt


class User(UserMixin, Timestamps, SurrogatePK, Model):
    email = Column(db.String(80), unique=True, nullable=False)
    password = Column(db.Binary(128), nullable=True)

    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)
