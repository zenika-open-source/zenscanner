from ninja import ModelSchema, Schema
from core.models import User


class MeSchema(ModelSchema):

    class Config:
        model = User
        model_fields = ['username', 'email']


class AccessTokenSchema(Schema):
    access_token: str


class LoginForm(Schema):
    username: str
    password: str


class RegisterForm(Schema):
    username: str
    email: str
    password: str
    passwordConfirmation: str
