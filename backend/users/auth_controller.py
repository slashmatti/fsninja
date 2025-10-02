# users/auth_controller.py
from ninja import Schema
from ninja_extra import api_controller, route
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.authentication import JWTAuth

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

@api_controller("/auth", tags=["Auth"])
class AuthController:
    @route.post("/register/", response={201: TokenResponse, 400: dict})
    def register(self, request, payload: RegisterSchema):
        if User.objects.filter(email=payload.email).exists():
            return 400, {"error": "Email already in use"}

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
            return 400, {"error": "Username already exists"}

    @route.post("/token/", response={200: TokenResponse, 401: dict})
    def login(self, request, payload: LoginSchema):
        try:
            user = User.objects.get(email=payload.email)
        except User.DoesNotExist:
            return 401, {"error": "Invalid credentials"}

        if not check_password(payload.password, user.password):
            return 401, {"error": "Invalid credentials"}

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

    @route.get("/me/", auth=JWTAuth())
    def me(self, request):
        return {
            "id": request.auth.id,
            "username": request.auth.username,
            "email": request.auth.email,
        }
