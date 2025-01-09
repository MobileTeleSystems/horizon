from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pydantic
import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import HWMResponseV1

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_get_hwm(hwm: HWM, sync_client: HorizonClientSync):
    response = sync_client.get_hwm(hwm.id)
    assert response == HWMResponseV1(
        id=hwm.id,
        namespace_id=hwm.namespace_id,
        name=hwm.name,
        type=hwm.type,
        value=hwm.value,
        entity=hwm.entity,
        expression=hwm.expression,
        description=hwm.description,
        changed_at=hwm.changed_at,
        changed_by=hwm.changed_by,
    )


def test_sync_client_get_hwm_missing(new_hwm: HWM, sync_client: HorizonClientSync):
    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"HWM with id={new_hwm.id!r} not found"),
    ) as e:
        sync_client.get_hwm(new_hwm.id)

    assert e.value.details == {
        "entity_type": "HWM",
        "field": "id",
        "value": new_hwm.id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_get_hwm_with_wrong_params(sync_client: HorizonClientSync):
    # hwm_id has wrong type, raw exception is raised
    with pytest.raises(requests.exceptions.HTTPError, match="422 Client Error"):
        sync_client.get_hwm("abc")
