from dataclasses import dataclass
from typing import AnyStr


@dataclass
class Credentials:
    login: AnyStr
    password: AnyStr

    @staticmethod
    def login_key_prefix() -> AnyStr:
        return "login"

    @staticmethod
    def password_key_prefix() -> AnyStr:
        return "password"
