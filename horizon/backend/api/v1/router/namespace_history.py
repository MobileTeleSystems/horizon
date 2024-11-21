# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.schemas.v1 import (
    NamespaceHistoryPaginateQueryV1,
    NamespaceHistoryResponseV1,
    PageResponseV1,
)

router = APIRouter(prefix="/namespace-history", tags=["Namespace History"], responses=get_error_responses())


@router.get(
    "/",
    summary="Paginate namespace history",
    dependencies=[Depends(current_user)],
)
async def paginate_hwm_history(
    pagination_args: Annotated[NamespaceHistoryPaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[NamespaceHistoryResponseV1]:
    pagination = await unit_of_work.namespace_history.paginate(**pagination_args.dict())
    return PageResponseV1[NamespaceHistoryResponseV1].from_pagination(pagination)
