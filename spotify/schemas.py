import marshmallow

from marshmallow import fields, EXCLUDE

import objects


class Page(marshmallow.Schema):
    class Meta:
        unknown = EXCLUDE

    limit = fields.Integer(required=True)
    offset = fields.Integer(required=True)
    total = fields.Integer(required=True)
    items = fields.List(fields.Dict, required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.Page(**data)


class Artist(marshmallow.Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.Artist(**data)


class SimpleTrack(marshmallow.Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.SimpleTrack(**data)


class SimpleAlbum(marshmallow.Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True)
    name = fields.String(required=True)
    artists = fields.List(fields.Nested(Artist), required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.SimpleAlbum(**data)


class Album(SimpleAlbum):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True)
    name = fields.String(required=True)
    artists = fields.List(fields.Nested(Artist), required=True)
    tracks = fields.Nested(Page, required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.Album(**data)


class Track(SimpleTrack):
    class Meta:
        unknown = EXCLUDE

    album = fields.Nested(SimpleAlbum, required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.Track(**data)


class SavedTrack(marshmallow.Schema):
    class Meta:
        unknown = EXCLUDE

    added_at = fields.DateTime(required=True)
    track = fields.Nested(Track, required=True)

    @marshmallow.post_load
    def make(self, data, **kwargs):
        return objects.SavedTrack(**data)
