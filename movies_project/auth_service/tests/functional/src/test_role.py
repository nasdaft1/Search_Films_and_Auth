import logging

import pytest

@pytest.mark.parametrize("query,index_paginator, status_code,  result", [
    ('/films/search?query=Star', [1, 2], 200, 2),
    ('/films/search?query=Star', [1, 50], 200, 50),
    ('/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', [1, 2], 200, 2),
    ('/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', [1, 50], 200, 46),

])
async def test_paginator_query(query, index_paginator, status_code, result, async_client):
    """Тестирование поиска"""
    await search_paginator(query, index_paginator, status_code, result, async_client)