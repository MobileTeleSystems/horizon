# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated

from horizon.backend.dependencies.stub import Stub
from horizon.backend.providers.auth import AuthProvider
from horizon.commons.errors import get_error_responses
from horizon.commons.errors.schemas import InvalidRequestSchema, NotAuthorizedSchema
from horizon.commons.schemas.v1 import AuthTokenResponseV1

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/token",
    summary="Get access token",
    responses=get_error_responses(include={NotAuthorizedSchema, InvalidRequestSchema}),
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_provider: Annotated[AuthProvider, Depends(Stub(AuthProvider))],
) -> AuthTokenResponseV1:
    token = await auth_provider.get_token(
        grant_type=form_data.grant_type,
        login=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes,
        client_id=form_data.client_id,
        client_secret=form_data.client_secret,
    )
    return AuthTokenResponseV1.parse_obj(token)
