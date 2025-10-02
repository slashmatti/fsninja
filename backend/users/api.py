# backend/users/api.py
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

router = Router()

# Register endpoint
class RegisterSchema(Schema):
    username: str
    email: str
    password: str

class RegisterResponse(Schema):
    id: int
    username: str
    email: str

@router.post("/register", response=RegisterResponse)
def register_user(request, payload: RegisterSchema):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already exists")
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already registered")

    user = User.objects.create(
        username=payload.username,
        email=payload.email,
        password=make_password(payload.password)
    )
    return RegisterResponse(id=user.id, username=user.username, email=user.email)

# Protected route
@router.get("/me", auth=JWTAuth())
def get_current_user(request):
    user = request.auth
    return {"id": user.id, "username": user.username, "email": user.email}
