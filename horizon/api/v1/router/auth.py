# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from horizon.dependencies.stub import Stub
from horizon.providers.auth import AuthProvider
from horizon_commons.errors import get_error_responses
from horizon_commons.errors.schemas import InvalidRequestSchema, NotAuthorizedSchema
from horizon_commons.schemas.v1 import AuthTokenSchemaV1

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/token",
    description="Get access token",
    responses=get_error_responses(include={NotAuthorizedSchema, InvalidRequestSchema}),
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_provider: Annotated[AuthProvider, Depends(Stub(AuthProvider))],
) -> AuthTokenSchemaV1:
    access_token, refresh_token = await auth_provider.get_tokens(
        grant_type=form_data.grant_type,
        username=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes,
        client_id=form_data.client_id,
        client_secret=form_data.client_secret,
    )
    return AuthTokenSchemaV1(access_token=access_token, refresh_token=refresh_token)
