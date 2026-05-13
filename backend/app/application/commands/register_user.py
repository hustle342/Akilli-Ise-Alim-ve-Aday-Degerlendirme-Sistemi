"""
RegisterUserCommand — CQRS: Command (Yazma İşlemi)
=====================================================
Kullanıcı kayıt işlemini yöneten command ve handler.
"""

from dataclasses import dataclass
from typing import Tuple

from werkzeug.security import generate_password_hash

from app.core.entities.user import User
from app.core.enums import UserRole
from app.application.dtos.dtos import UserDTO
from app.infrastructure.config import settings


@dataclass
class RegisterUserCommand:
    """Kullanıcı kayıt komutu."""
    full_name: str
    email: str
    password: str
    role: str = "candidate"
    bootstrap_code: str = ""


class RegisterUserHandler:
    """
    CQRS Command Handler — Kullanıcı kaydı.

    Sorumluluklar:
    - Validasyon
    - Şifre hashleme
    - Veritabanına yazma
    - Domain event yayınlama
    """

    def __init__(self, user_repository, event_bus=None):
        self._user_repo = user_repository
        self._event_bus = event_bus

    def handle(self, command: RegisterUserCommand) -> Tuple[UserDTO | None, str | None]:
        """
        Kullanıcı kaydını gerçekleştir.

        Returns:
            Tuple[UserDTO | None, str | None]: (sonuç, hata_mesajı)
        """
        # Validasyon
        full_name = command.full_name.strip()
        email = command.email.strip().lower()

        if len(full_name) < 2:
            return None, "full_name en az 2 karakter olmalidir"
        if "@" not in email:
            return None, "gecerli bir email girilmelidir"
        if not isinstance(command.password, str) or len(command.password) < 8:
            return None, "password en az 8 karakter olmalidir"

        try:
            role = UserRole(command.role.strip().lower())
        except ValueError:
            return None, "role degeri candidate/hr/admin olmali"

        if role in {UserRole.HR, UserRole.ADMIN}:
            if command.bootstrap_code != settings.ADMIN_BOOTSTRAP_CODE:
                return None, "hr/admin kaydi icin bootstrap code gecersiz"

        # Mevcut kullanıcı kontrolü
        existing = self._user_repo.get_by_email(email)
        if existing is not None:
            return None, "bu email zaten kayitli"

        # Kullanıcı oluşturma
        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(command.password),
            role=role,
        )
        self._user_repo.add(user)
        self._user_repo.commit()
        self._user_repo.refresh(user)

        # Event yayınla (Observer + ESB)
        if self._event_bus:
            self._event_bus.publish("user.registered", {
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
            })

        return UserDTO(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role.value,
        ), None
