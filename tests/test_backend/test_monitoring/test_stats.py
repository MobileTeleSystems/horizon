# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import textwrap

import pytest
from httpx import AsyncClient

from horizon.backend.db.models.hwm import HWM
from horizon.backend.db.models.namespace import Namespace
from horizon.backend.db.models.user import User

pytestmark = [pytest.mark.asyncio]


async def test_stats_empty(test_client: AsyncClient):
    response = await test_client.get("/monitoring/stats")
    assert response.status_code == 200
    expected = textwrap.dedent(
        """
            # HELP horizon_user_count Number of users registered in Horizon database
            # TYPE horizon_user_count gauge
            horizon_user_count{app_name="horizon"} 0.0
            # HELP horizon_namespace_count Number of namespaces created in Horizon database
            # TYPE horizon_namespace_count gauge
            horizon_namespace_count{app_name="horizon"} 0.0
            # HELP horizon_hwm_count Number of HWMs created in Horizon database
            # TYPE horizon_hwm_count gauge
            horizon_hwm_count{app_name="horizon"} 0.0
            """,
    ).lstrip()
    assert response.text == expected


@pytest.mark.parametrize("settings", [{"server": {"prometheus": {"labels": {"a": "b", "c": "d"}}}}], indirect=True)
async def test_stats_with_custom_labels(test_client: AsyncClient):
    response = await test_client.get("/monitoring/stats")
    assert response.status_code == 200
    expected = textwrap.dedent(
        """
            # HELP horizon_user_count Number of users registered in Horizon database
            # TYPE horizon_user_count gauge
            horizon_user_count{a="b",app_name="horizon",c="d"} 0.0
            # HELP horizon_namespace_count Number of namespaces created in Horizon database
            # TYPE horizon_namespace_count gauge
            horizon_namespace_count{a="b",app_name="horizon",c="d"} 0.0
            # HELP horizon_hwm_count Number of HWMs created in Horizon database
            # TYPE horizon_hwm_count gauge
            horizon_hwm_count{a="b",app_name="horizon",c="d"} 0.0
            """,
    ).lstrip()
    assert response.text == expected


@pytest.mark.parametrize("users", [(7, {})], indirect=True)
@pytest.mark.parametrize("namespaces", [(3, {})], indirect=True)
@pytest.mark.parametrize("hwms", [(12, {})], indirect=True)
async def test_stats(
    test_client: AsyncClient,
    users: list[User],
    namespaces: list[Namespace],
    hwms: list[HWM],
):
    response = await test_client.get("/monitoring/stats")
    assert response.status_code == 200

    # hwm namespace creates separated namespace, namespace creates separate user
    # so number of users and namespaces is +1 of described in current test params
    expected = textwrap.dedent(
        """
            # HELP horizon_user_count Number of users registered in Horizon database
            # TYPE horizon_user_count gauge
            horizon_user_count{app_name="horizon"} 8.0
            # HELP horizon_namespace_count Number of namespaces created in Horizon database
            # TYPE horizon_namespace_count gauge
            horizon_namespace_count{app_name="horizon"} 4.0
            # HELP horizon_hwm_count Number of HWMs created in Horizon database
            # TYPE horizon_hwm_count gauge
            horizon_hwm_count{app_name="horizon"} 12.0
            """,
    ).lstrip()
    assert response.text == expected
