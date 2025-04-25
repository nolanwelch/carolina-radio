from .song import Song


__authors__ = ["David Foss", "Gabrian Chua", "Nolan Welch", "Rohan Kashyap"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class NowPlayingSong(Song):
    position: float
