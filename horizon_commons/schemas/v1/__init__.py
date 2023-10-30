# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from horizon_commons.schemas.v1.auth import AuthTokenResponseV1
from horizon_commons.schemas.v1.hwm import ReadHWMSchemaV1, WriteHWMSchemaV1
from horizon_commons.schemas.v1.hwm_history import ReadHWMHistorySchemaV1
from horizon_commons.schemas.v1.namespace import (
    CreateNamespaceRequestV1,
    NamespaceResponseV1,
    PaginateNamespaceQueryV1,
    UpdateNamespaceRequestV1,
)
from horizon_commons.schemas.v1.pagination import (
    PageMetaResponseV1,
    PageResponseV1,
    PaginateQueryV1,
)
