from ninja import Router, Schema
from core.utils.security import AuthBearer, BasicAuth
from .schemas import (
    MeSchema,
    LoginForm,
    RegisterForm,
    AccessTokenSchema
)
from django.core.exceptions import ObjectDoesNotExist
from core.models import User, UserSession
from django.db.utils import IntegrityError
from django.core.validators import validate_email
from django.conf import settings
from django.core.exceptions import ValidationError
import jwt
import datetime

router = Router(tags=["Authentication"])


class Message(Schema):
    message: str


@router.get('/me', response=MeSchema, auth=[AuthBearer(), BasicAuth()])
def get_user_information(request):
    return request.user


@router.get('/logout', auth=[AuthBearer()])
def logout(request):
    request.session.delete()
    return {}


@router.post('/login', response={401: Message, 200: AccessTokenSchema})
def login(request, data: LoginForm):
    try:
        user = User.objects.get(username=data.username)
        if user.is_good_password(data.password):
            session = UserSession(user=user)
            session.save()
            encoded_jwt = jwt.encode({
                "sub": str(user.id),
                "jti": str(session.id),
                "iat": int(datetime.datetime.now().timestamp()),
                "exp": int(session.deleted_at.timestamp()),
            }, settings.SECRET_KEY, algorithm="HS256")
            return 200, {"access_token": encoded_jwt}
    except ObjectDoesNotExist:
        pass
    return 401, {'message': "Unauthorized"}


@router.post('/register', response={422: Message, 200: Message, 403: Message})
def register(request, data: RegisterForm):

    if not settings.REGISTRATION_ENABLED:
        return 403, {'message': 'User registration disabled.'}

    if settings.REGISTRATION_DOMAINS != ['']:
        if data.email.split('@')[-1] not in settings.REGISTRATION_DOMAINS:
            return 403, {'message': 'Domain not allowed'}

    if data.password == data.passwordConfirmation:
        try:
            validate_email(data.email)
        except ValidationError:
            return 422, {'message': 'Email is not valid'}
        else:
            try:
                user = User(username=data.username, email=data.email)
                user.set_password(data.password)
                user.save()
            except IntegrityError:
                pass

            finally:
                return 200, {"message": "Success! You will receive an email to confirm your account"}
    else:
        return 422, {'message': 'Unprocessable Entity'}
