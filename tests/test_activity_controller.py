import jwt


def _auth_header_for_user(user_id: int = 1):
    token = jwt.encode({"user_id": user_id}, "test-jwt-key", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def test_click_requires_auth(client):
    r = client.post("/activity/click", json={"item_id": 1})
    assert r.status_code in (401, 403)


def test_click_ok(client, db_session):
    # seed item
    from repos.item import ItemRepo
    from models.item import ItemModel

    ItemRepo(db_session).create(ItemModel(item_id=1, item_name="Pizza", cuisine="Italian"))

    r = client.post("/activity/click", json={"item_id": 1}, headers=_auth_header_for_user(7))
    assert r.status_code == 200


def test_order_ok(client, db_session):
    from repos.item import ItemRepo
    from models.item import ItemModel

    ItemRepo(db_session).create(ItemModel(item_id=2, item_name="Ramen", cuisine="Japanese"))

    r = client.post("/activity/order", json={"item_id": 2}, headers=_auth_header_for_user(8))
    assert r.status_code == 200
    body = r.json()
    assert body["item_id"] == 2
    assert "order_id" in body

