from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.kernels.jwt_exceptions import DecodeException, TokenExpiredException

from app.libs.jwt_management import extract_payload_from_token


class JWTManager(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTManager, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTManager, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authorization token.")
            if not self.verify_jwt(credentials.credentials, request):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization token.")

    def verify_jwt(self, jwt: str, request) -> bool:

        try:
            payload = extract_payload_from_token(jwt)
        except TokenExpiredException:
            raise HTTPException(status_code=401, detail="Expired authorization token.")
        except DecodeException:
            raise HTTPException(status_code=403, detail="Invalid authorization token.")
        if payload:
            applications = payload.get('applications')
            if not applications:
                raise HTTPException(status_code=403, detail="Invalid authorization token.")

            authenticator = applications.get('authenticator')
            if not authenticator:
                raise HTTPException(status_code=401, detail="Not enough rights")

            request.user_applications = applications
            return True
        return False
