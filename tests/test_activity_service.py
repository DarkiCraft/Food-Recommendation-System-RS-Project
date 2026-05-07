import pytest

from models.item import ItemModel
from models.order import OrderModel
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.order import OrderRepo
from repos.rating import RatingRepo
from schemas.activity import ClickRequest, OrderRequest, RateRequest
from services.activity import ActivityService


def _seed_item(db_session, item_id: int = 1):
    repo = ItemRepo(db_session)
    item = ItemModel(item_id=item_id, item_name="Burger", cuisine="Fast Food")
    repo.create(item)
    return item


def test_click_creates_interaction(db_session):
    _seed_item(db_session, item_id=1)

    service = ActivityService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        order_repo=OrderRepo(db_session),
        rating_repo=RatingRepo(db_session),
    )

    service.click(ClickRequest(item_id=1), user_id=10)

    interactions = InteractionRepo(db_session).get_by_user(10)
    assert len(interactions) == 1
    assert interactions[0].item_id == 1


def test_click_missing_item_raises(db_session):
    service = ActivityService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        order_repo=OrderRepo(db_session),
        rating_repo=RatingRepo(db_session),
    )

    with pytest.raises(ValueError):
        service.click(ClickRequest(item_id=999), user_id=10)


def test_order_creates_order_and_interaction(db_session):
    _seed_item(db_session, item_id=2)

    service = ActivityService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        order_repo=OrderRepo(db_session),
        rating_repo=RatingRepo(db_session),
    )

    resp = service.order(OrderRequest(item_id=2), user_id=11)
    assert resp.item_id == 2
    assert resp.order_id > 0

    orders = OrderRepo(db_session).get_by_user(11)
    assert len(orders) == 1
    assert isinstance(orders[0], OrderModel)

    interactions = InteractionRepo(db_session).get_by_user_item(11, 2)
    assert len(interactions) >= 1


def test_rate_creates_rating(db_session):
    _seed_item(db_session, item_id=3)

    order_repo = OrderRepo(db_session)
    rating_repo = RatingRepo(db_session)

    service = ActivityService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        order_repo=order_repo,
        rating_repo=rating_repo,
    )

    order_resp = service.order(OrderRequest(item_id=3), user_id=12)
    service.rate(RateRequest(order_id=order_resp.order_id, rating=5), user_id=12)

    rating = rating_repo.get_by_order(order_resp.order_id)
    assert rating is not None
    assert rating.rating == 5


def test_rate_wrong_user_raises(db_session):
    _seed_item(db_session, item_id=4)

    service = ActivityService(
        interaction_repo=InteractionRepo(db_session),
        item_repo=ItemRepo(db_session),
        order_repo=OrderRepo(db_session),
        rating_repo=RatingRepo(db_session),
    )

    order_resp = service.order(OrderRequest(item_id=4), user_id=20)
    with pytest.raises(ValueError):
        service.rate(RateRequest(order_id=order_resp.order_id, rating=3), user_id=21)

