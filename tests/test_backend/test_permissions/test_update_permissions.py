# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.backend.db.models import Namespace, NamespaceUserRole

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


@pytest.mark.parametrize(
    "user_with_role, expected_status, expected_response",
    [
        (
            NamespaceUserRole.MAINTAINER,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": f"Permission denied. User has role MAINTAINER but action requires at least OWNER.",
                    "details": {
                        "required_role": "OWNER",
                        "actual_role": "MAINTAINER",
                    },
                }
            },
        ),
        (
            NamespaceUserRole.DEVELOPER,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": f"Permission denied. User has role DEVELOPER but action requires at least OWNER.",
                    "details": {
                        "required_role": "OWNER",
                        "actual_role": "DEVELOPER",
                    },
                }
            },
        ),
        (
            NamespaceUserRole.GUEST,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": f"Permission denied. User has role GUEST but action requires at least OWNER.",
                    "details": {
                        "required_role": "OWNER",
                        "actual_role": "GUEST",
                    },
                }
            },
        ),
    ],
    indirect=["user_with_role"],
)
async def test_update_permissions_denied(
    namespace: Namespace,
    user_with_role: None,
    expected_status: int,
    expected_response: dict,
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        f"v1/namespace/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response
