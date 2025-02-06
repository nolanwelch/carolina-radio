# https://github.com/unc-csxl/csxl.unc.edu/blob/main/backend/entities/entity_base.py
"""Abstract superclass of all entities in the application.

There is no reason to instantiate this class directly. Instead, look toward the child classes.
Additionally, import from the top-level entities file which indexes all entity implementations.
"""


from sqlalchemy.orm import DeclarativeBase


__authors__ = ["Kris Jordan"]
__copyright__ = "Copyright 2023"
__license__ = "MIT"


class EntityBase(DeclarativeBase):
    pass
