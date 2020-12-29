from notion import client

import auth


def notion_client() -> client.NotionClient:
    return client.NotionClient(token_v2=auth.get_token())
