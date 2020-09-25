class Artist:
    def __init__(self, name):
        self.name = name


class SimpleTrack:
    def __init__(self, id):
        self.id = id


class SimpleAlbum:
    def __init__(self, id, name, artists):
        self.id = id
        self.name = name
        self.artists = artists


class Album:
    def __init__(self, id, name, artists, tracks):
        self.id = id
        self.name = name
        self.artists = artists
        self.tracks = tracks

    def __str__(self):
        return '{} [{}]'.format(
            self.name,
            ', '.join([artist.name for artist in self.artists]),
        )


class Track:
    def __init__(self, id, album):
        self.id = id
        self.album = album


class SavedTrack:
    def __init__(self, added_at, track):
        self.added_at = added_at
        self.track = track


class Page:
    def __init__(self, limit, offset, total, items):
        self.limit = limit
        self.offset = offset
        self.total = total
        self.items = items
