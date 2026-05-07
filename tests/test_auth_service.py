import os

import jwt
import pytest

from models.user import UserModel
from repos.user import UserRepo
from schemas.auth import SignupRequest, LoginRequest
from services.auth import AuthService


def test_signup_creates_user(db_session):
    repo = UserRepo(db_session)
    service = AuthService(repo)

    resp = service.signup(SignupRequest(user_name="u1", email="u1@example.com", password="pw"))

    assert resp.user_id > 0
    assert resp.user_name == "u1"
    assert resp.email == "u1@example.com"

    user = repo.get_by_email("u1@example.com")
    assert isinstance(user, UserModel)
    assert user.user_name == "u1"
    assert user.password_hash != b"pw"


def test_login_returns_jwt_token(db_session):
    os.environ["JWT_KEY"] = "test-jwt-key"
    repo = UserRepo(db_session)
    service = AuthService(repo)

    service.signup(SignupRequest(user_name="u2", email="u2@example.com", password="pw2"))
    login = service.login(LoginRequest(email="u2@example.com", password="pw2"))

    assert login.token_type == "bearer"
    payload = jwt.decode(login.access_token, os.environ["JWT_KEY"], algorithms=["HS256"])
    assert "user_id" in payload


def test_login_bad_password_raises(db_session):
    repo = UserRepo(db_session)
    service = AuthService(repo)
    service.signup(SignupRequest(user_name="u3", email="u3@example.com", password="pw3"))

    with pytest.raises(ValueError):
        service.login(LoginRequest(email="u3@example.com", password="wrong"))


def test_login_missing_user_raises(db_session):
    repo = UserRepo(db_session)
    service = AuthService(repo)

    with pytest.raises(ValueError):
        service.login(LoginRequest(email="missing@example.com", password="pw"))

