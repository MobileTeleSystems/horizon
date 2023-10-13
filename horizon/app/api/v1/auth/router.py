# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.errors import get_error_responses
from app.api.errors.schemas import InvalidRequestSchema, NotAuthorizedSchema
from app.api.v1.auth.schemas import AuthTokenSchema
from app.dependencies.stub import Stub
from app.providers.auth import AuthProvider

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/token",
    description="Get access token",
    responses=get_error_responses(include={NotAuthorizedSchema, InvalidRequestSchema}),
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_provider: Annotated[AuthProvider, Depends(Stub(AuthProvider))],
) -> AuthTokenSchema:
    access_token, refresh_token = await auth_provider.get_tokens(
        grant_type=form_data.grant_type,
        username=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes,
        client_id=form_data.client_id,
        client_secret=form_data.client_secret,
    )
    return AuthTokenSchema(access_token=access_token, refresh_token=refresh_token)
