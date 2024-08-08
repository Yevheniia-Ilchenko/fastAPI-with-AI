from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy


# class OAuth2PasswordRequestFormEmail(OAuth2PasswordRequestForm):
#     def __init__(self, grant_type: str = None, username: str = None, password: str = None, scope: str = "", client_id: str = None, client_secret: str = None):
#         super().__init__(grant_type=grant_type, username=username, password=password, scope=scope, client_id=client_id, client_secret=client_secret)
#         self.email = username


cookie_transport = CookieTransport(cookie_name="posts", cookie_max_age=3600)

SECRET = "SECRET"   # TODO add secretkey -> .env


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)





