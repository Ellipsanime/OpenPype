from dataclasses import dataclass


@dataclass
class Credentials:
    login: str
    password: str

    def is_empty(self) -> bool:
        return not (self.login and self.password)

    @staticmethod
    def login_key_prefix() -> str:
        return "login"

    @staticmethod
    def password_key_prefix() -> str:
        return "password"
