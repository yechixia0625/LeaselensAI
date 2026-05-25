from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.api.deps import provide_demo_auth_service, provide_settings
from src.config.settings import Settings
from src.models.schemas.auth import DemoLoginRequest, DemoSessionResponse
from src.services.demo_auth import DemoAuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=DemoSessionResponse)
async def login(
    request: DemoLoginRequest,
    response: Response,
    settings: Settings = Depends(provide_settings),
    auth: DemoAuthService = Depends(provide_demo_auth_service),
) -> DemoSessionResponse:
    if not settings.demo_auth_enabled:
        return DemoSessionResponse(
            authenticated=True, username="demo-auth-disabled", authEnabled=False
        )

    if not auth.verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    response.set_cookie(
        key=settings.demo_auth_cookie_name,
        value=auth.issue_cookie_value(),
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return DemoSessionResponse(
        authenticated=True, username=request.username, authEnabled=True
    )


@router.post("/logout", response_model=DemoSessionResponse)
async def logout(
    response: Response,
    settings: Settings = Depends(provide_settings),
) -> DemoSessionResponse:
    response.delete_cookie(
        key=settings.demo_auth_cookie_name,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
    return DemoSessionResponse(authenticated=False, username=None, authEnabled=True)


@router.get("/session", response_model=DemoSessionResponse)
async def session_status(
    request: Request,
    settings: Settings = Depends(provide_settings),
    auth: DemoAuthService = Depends(provide_demo_auth_service),
) -> DemoSessionResponse:
    if not settings.demo_auth_enabled:
        return DemoSessionResponse(
            authenticated=True, username="demo-auth-disabled", authEnabled=False
        )

    username = auth.read_cookie_value(request.cookies.get(settings.demo_auth_cookie_name))
    return DemoSessionResponse(
        authenticated=username is not None,
        username=username,
        authEnabled=True,
    )
