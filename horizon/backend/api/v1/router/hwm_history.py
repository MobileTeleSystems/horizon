# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.schemas.v1 import (
    HWMHistoryPaginateQueryV1,
    HWMHistoryResponseV1,
    PageResponseV1,
)

router = APIRouter(prefix="/hwm-history", tags=["HWM History"], responses=get_error_responses())


@router.get(
    "/",
    summary="Paginate HWM history",
    dependencies=[Depends(current_user)],
)
async def paginate_hwm_history(
    pagination_args: Annotated[HWMHistoryPaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[HWMHistoryResponseV1]:
    pagination = await unit_of_work.hwm_history.paginate(**pagination_args.dict())
    return PageResponseV1[HWMHistoryResponseV1].from_pagination(pagination)
