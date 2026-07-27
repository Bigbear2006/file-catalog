import pytest
from httpx import AsyncClient


@pytest.mark.order(after='test_file')
@pytest.mark.anyio
async def test_admin(
    client: AsyncClient,
    admin_headers: dict[str, str],
    x_candidate_id: str,
    candidate_ip: str,
) -> None:
    rsp = await client.delete(
        f'/admin/candidates/{x_candidate_id}/progress', headers=admin_headers
    )
    assert rsp.status_code == 200
    assert rsp.json()['reset'] is True

    rsp = await client.delete(
        f'/admin/clients/{candidate_ip}/throttling', headers=admin_headers
    )
    assert rsp.status_code == 200
    assert rsp.json()['reset'] is True
