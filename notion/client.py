import cachetools

from notion import client

import auth


@cachetools.cached(cachetools.Cache(maxsize=1))
def notion_client() -> client.NotionClient:
    return client.NotionClient(token_v2=auth.get_token())
