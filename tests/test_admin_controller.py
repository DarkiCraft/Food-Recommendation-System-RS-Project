def test_admin_stats_requires_admin_token(client):
    r = client.get("/admin/stats")
    assert r.status_code in (401, 403)


def test_admin_stats_with_token(client):
    import os

    r = client.get("/admin/stats", headers={"X-Admin-Token": os.environ["ADMIN_API_KEY"]})
    assert r.status_code == 200
    body = r.json()
    assert {"total_users", "total_items", "total_interactions", "total_orders"} <= set(body.keys())

