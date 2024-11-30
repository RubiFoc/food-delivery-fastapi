from fastapi_users.authentication import CookieTransport, AuthenticationBackend, BearerTransport
from fastapi_users.authentication import JWTStrategy

from config import SECRET

cookie_transport = CookieTransport(cookie_name="your_cookie_name", cookie_secure=True, cookie_samesite="none")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    # transport=BearerTransport(tokenUrl="auth/jwt/login"),
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
