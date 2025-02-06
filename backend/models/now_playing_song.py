from .song import SongModel


__authors__ = ["David Foss", "Gabrian Chua", "Nolan Welch", "Rohan Kashyap"]
__copyright__ = "Copyright 2025"
__license__ = "MIT"


class NowPlayingSongModel(SongModel):
    position: float
