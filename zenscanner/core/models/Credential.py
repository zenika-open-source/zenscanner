from django.db import models
from uuid import uuid4
from core.models import User
import glob
import os
import importlib
from Crypto.Cipher import AES
from Crypto import Random
import binascii
from django.conf import settings

BS = 16
KEY = settings.SECRET_KEY[:32]


def unpad(data):
    return data[0:-data[-1]]


def pad(data):
    data = data.encode('utf-8') if type(data) == str else data
    return data + bytes([BS - len(data) % BS for _ in range(BS - len(data) % BS)])


def encrypt(value):
    raw = pad(value)
    outs = []
    for bloc_idx in range(0, len(raw), BS):
        data = raw[bloc_idx: bloc_idx + BS]
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(KEY.encode("utf8"), AES.MODE_CBC, iv)
        outs.append(iv + cipher.encrypt(data))
    return binascii.hexlify(b"".join(outs)).decode()


def decrypt(enc_value):
    enc = binascii.unhexlify(enc_value)
    outs = []
    try:
        for bloc_idx in range(0, len(enc), 2 * BS):

            iv = enc[bloc_idx:bloc_idx + BS]
            data = enc[bloc_idx + BS:bloc_idx + 2 * BS]
            cipher = AES.new(KEY.encode("utf8"), AES.MODE_CBC, iv)
            outs.append(cipher.decrypt(data))
    except ValueError:
        # TODO: Mail en cas de soucis, à penser une fois le mailing done /!\
        return ""
    return unpad(b"".join(outs)).decode()


MODULES_LOCATIONS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins/credentials")


def load_credentials_types():
    types = {}
    for file in glob.glob('{}/*.py'.format(MODULES_LOCATIONS)):
        name = os.path.basename(file)[:-3]
        if name != "__init__":
            module = importlib.import_module("core.models.plugins.credentials.{}".format(name))
            module_class = getattr(module, name)
            types[module_class.name] = module_class
    return types


CREDENTIALS_TYPES = load_credentials_types()


class Credential(models.Model):

    label = models.TextField()
    type = models.TextField()
    _uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_column='uuid')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default="-1")
    _raw_value = models.TextField(default="", db_column='raw_value')
    allow_sync = models.BooleanField(default=True)

    @property
    def uuid(self):
        return "" if self.type in ['PublicGit', 'PublicSvn'] else self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def raw_value(self):
        return "" if self._raw_value == "" else decrypt(self._raw_value)

    @raw_value.setter
    def raw_value(self, value):
        self._raw_value = encrypt(value)

    def get_instance(self):
        return CREDENTIALS_TYPES.get(self.type, False)(self)

    def is_valid_credential_type(self):
        return self.type in CREDENTIALS_TYPES

    def save(self, *args, **kwargs):
        if self.is_valid_credential_type():
            instance = self.get_instance()
            if instance.validate():
                super(Credential, self).save(*args, **kwargs)
            else:
                raise KeyError
        else:
            raise KeyError
