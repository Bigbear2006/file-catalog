import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_file(
    client: AsyncClient, candidate_headers: dict[str, str]
) -> None:
    rsp = await client.get('/files/names', headers=candidate_headers)
    assert rsp.status_code == 200
    names = rsp.json()['names']
    assert isinstance(names, list)
    assert 3 <= len(names) <= 9

    if len(names) > 3:
        names = names[:3]

    rsp = await client.post(
        '/files/download', json={'names': names}, headers=candidate_headers
    )
    assert rsp.status_code == 200
    assert rsp.headers.get('Content-Type') == 'application/zip'

    rsp = await client.post(
        '/files/downloaded', json={'names': names}, headers=candidate_headers
    )
    assert rsp.status_code == 200
    data = rsp.json()
    assert data['marked'] == len(names)
    assert data['already_marked'] == 0
