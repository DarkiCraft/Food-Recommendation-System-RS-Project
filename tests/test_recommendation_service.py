import os

import pytest

from datetime import datetime, timezone

from models.interaction import InteractionModel, InteractionType
from models.item import ItemModel
from models.user import UserModel
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.user import UserRepo
from schemas.recommend import RecommendRequest
from services.recommend import RecommendationService


@pytest.fixture(autouse=True)
def _recommend_env(tmp_path):
    os.environ.setdefault("EMBEDDING_DIM", "8")
    os.environ.setdefault("EPOCHS", "1")
    os.environ.setdefault("LEARNING_RATE", "0.001")
    os.environ.setdefault("W_NCF", "0.0")  # keep tests fast/deterministic
    os.environ.setdefault("W_SVD", "0.0")
    os.environ.setdefault("W_CONTENT", "0.0")
    os.environ.setdefault("W_POPULARITY", "1.0")  # only popularity matters in these tests
    yield


def _seed_users_items(db_session):
    user_repo = UserRepo(db_session)
    item_repo = ItemRepo(db_session)

    user_repo.create(
        UserModel(
            user_id=1,
            user_name="u",
            email="u@e.com",
            password_hash=b"x",
            signup_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
    )

    for i in range(1, 6):
        item_repo.create(ItemModel(item_id=i, item_name=f"Item {i}", cuisine="X"))


def _seed_interactions(db_session, user_id: int):
    repo = InteractionRepo(db_session)
    # Make item 2 most popular, then 1, then 3
    repo.create(InteractionModel(user_id=user_id, item_id=2, interaction_type=InteractionType.CLICK, timestamp=datetime(2020, 1, 1, tzinfo=timezone.utc)))
    repo.create(InteractionModel(user_id=user_id, item_id=2, interaction_type=InteractionType.CLICK, timestamp=datetime(2020, 1, 2, tzinfo=timezone.utc)))
    repo.create(InteractionModel(user_id=user_id, item_id=1, interaction_type=InteractionType.CLICK, timestamp=datetime(2020, 1, 3, tzinfo=timezone.utc)))
    repo.create(InteractionModel(user_id=user_id, item_id=3, interaction_type=InteractionType.CLICK, timestamp=datetime(2020, 1, 4, tzinfo=timezone.utc)))


def test_recommend_single_k_returns_recommendresponse(db_session):
    _seed_users_items(db_session)
    _seed_interactions(db_session, user_id=1)

    service = RecommendationService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        user_repo=UserRepo(db_session),
    )

    result = service.recommend(RecommendRequest(k=[3]), user_id=1)
    assert hasattr(result, "recommendations")
    assert result.recommendations[:2] == [2, 1]


def test_recommend_multi_k_returns_slices(db_session):
    _seed_users_items(db_session)
    _seed_interactions(db_session, user_id=1)

    service = RecommendationService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        user_repo=UserRepo(db_session),
    )

    result = service.recommend(RecommendRequest(k=[3, 5]), user_id=1)
    assert isinstance(result, dict)
    assert result["3"] == [2, 1, 3]
    assert result["5"][:3] == [2, 1, 3]


def test_recommend_cold_start_uses_popularity(db_session):
    _seed_users_items(db_session)
    # no interactions for user 1; popularity model will have no counts and return []

    service = RecommendationService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        user_repo=UserRepo(db_session),
    )

    result = service.recommend(RecommendRequest(k=[3, 5]), user_id=1)
    assert isinstance(result, dict)
    assert result["3"] == []
    assert result["5"] == []

