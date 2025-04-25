from backend.models.listener import Listener
from backend.models.radio import Radio

__authors__ = ["David Foss"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class ListenerDetails(Listener):
    radio: Radio
