# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import HWMResponseV1, HWMUpdateRequestV1

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, User

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_update_hwm_update_existing_full(
    new_hwm: HWM,
    hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_update = HWMUpdateRequestV1(
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )
    response = sync_client.update_hwm(hwm.id, to_update)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"changed_at"}) == dict(
        id=hwm.id,
        namespace_id=hwm.namespace_id,
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
        changed_by=user.username,
    )


def test_sync_client_update_hwm_update_existing_minimal(
    new_hwm: HWM,
    hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_update = HWMUpdateRequestV1(value=new_hwm.value)
    response = sync_client.update_hwm(hwm.id, to_update)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"changed_at"}) == dict(
        id=hwm.id,
        namespace_id=hwm.namespace_id,
        name=hwm.name,
        type=hwm.type,
        value=new_hwm.value,
        entity=hwm.entity,
        expression=hwm.expression,
        description=hwm.description,
        changed_by=user.username,
    )


def test_sync_client_update_hwm_missing(
    sync_client: HorizonClientSync,
    new_hwm: HWM,
):
    to_update = HWMUpdateRequestV1(value=new_hwm.value)

    with pytest.raises(EntityNotFoundError, match=f"HWM with id={new_hwm.id!r} not found") as e:
        sync_client.update_hwm(new_hwm.id, to_update)

    assert e.value.details == {
        "entity_type": "HWM",
        "field": "id",
        "value": new_hwm.id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_update_hwm_malformed(new_hwm: HWM, sync_client: HorizonClientSync):
    to_update = HWMUpdateRequestV1(value=new_hwm.value)

    with pytest.raises(requests.exceptions.HTTPError, match="405 Client Error: Method Not Allowed for url"):
        sync_client.update_hwm("", to_update)
