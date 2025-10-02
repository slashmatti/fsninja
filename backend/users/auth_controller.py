from ninja import Schema
from ninja_extra import api_controller, route
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.authentication import JWTAuth
from typing import Optional

User = get_user_model()

# --- Schemas ---

class RegisterSchema(Schema):
    username: str
    email: str
    password: str

class LoginSchema(Schema):
    email: str
    password: str

class TokenResponse(Schema):
    access: str
    refresh: str
    id: int
    username: str
    email: str

class RefreshRequest(Schema):
    refresh: str

class UserSchema(Schema):
    id: int
    username: str
    email: str


# --- Controller ---
@api_controller("/auth", tags=["Auth"])
class AuthController:
    @route.post("/register/", response={201: TokenResponse, 400: dict})
    def register(self, request, payload: RegisterSchema):
        """
        Register a new user and return JWT tokens + user info.
        """
        try:
            user = User.objects.create(
                username=payload.username,
                email=payload.email,
                password=make_password(payload.password),
            )
            refresh = RefreshToken.for_user(user)
            return 201, {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        except IntegrityError:
            return 400, {"error": "Username or email already exists."}

    @route.post("/token/", response={200: TokenResponse, 401: dict})
    def login(self, request, payload: LoginSchema):
        """
        Login using email + password and return JWT tokens.
        """
        try:
            user = User.objects.get(email=payload.email)
        except User.DoesNotExist:
            return 401, {"error": "Invalid credentials."}

        if not check_password(payload.password, user.password):
            return 401, {"error": "Invalid credentials."}

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

    @route.post("/refresh/", response={200: dict, 401: dict})
    def refresh_token(self, request, payload: RefreshRequest):
        """
        Refresh the access token using a refresh token.
        """
        try:
            refresh = RefreshToken(payload.refresh)
            return {"access": str(refresh.access_token)}
        except Exception:
            return 401, {"error": "Invalid or expired refresh token."}

    @route.get("/me/", response=UserSchema, auth=JWTAuth())
    def me(self, request):
        """
        Get the current authenticated user.
        """
        return request.auth
