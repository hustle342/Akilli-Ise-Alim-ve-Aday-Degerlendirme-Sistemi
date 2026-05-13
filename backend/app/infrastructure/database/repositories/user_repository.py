"""
User Repository — Infrastructure Layer
========================================
IUserRepository arayüzünün SQLAlchemy implementasyonu.
"""

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.entities.user import User
from app.core.enums import UserRole
from app.core.interfaces.repositories import IUserRepository


class UserRepository(IUserRepository):
    """SQLAlchemy tabanlı User repository implementasyonu."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, entity_id: int):
        return self._session.get(User, entity_id)

    def get_all(self) -> list:
        return self._session.query(User).all()

    def get_by_email(self, email: str):
        return self._session.query(User).filter(User.email == email).first()

    def count_by_role(self, role: UserRole) -> int:
        return (
            self._session.query(User).filter(User.role == role).count()
        )

    def add(self, entity) -> None:
        self._session.add(entity)

    def delete(self, entity) -> None:
        self._session.delete(entity)

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity) -> None:
        self._session.refresh(entity)
