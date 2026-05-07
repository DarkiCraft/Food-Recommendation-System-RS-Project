def test_recommendations_single_k_returns_recommendations(client):
    import dependencies as deps

    def _user_override():
        return 1

    class _FakeService:
        def recommend(self, request, user_id: int):
            return [10, 20, 30][: request.k[0]]

    def _svc_override():
        return _FakeService()

    client.app.dependency_overrides[deps.get_current_user] = _user_override
    client.app.dependency_overrides[deps.get_recommendation_service] = _svc_override

    r = client.get("/recommendations?k=2", headers={"Authorization": "Bearer x"})
    assert r.status_code == 200
    assert r.json() == {"recommendations": [10, 20]}


def test_recommendations_multi_k_returns_mapping(client):
    import dependencies as deps

    def _user_override():
        return 1

    class _FakeService:
        def recommend(self, request, user_id: int):
            return {"3": [1, 2, 3], "5": [1, 2, 3, 4, 5]}

    def _svc_override():
        return _FakeService()

    client.app.dependency_overrides[deps.get_current_user] = _user_override
    client.app.dependency_overrides[deps.get_recommendation_service] = _svc_override

    r = client.get("/recommendations?k=3&k=5", headers={"Authorization": "Bearer x"})
    assert r.status_code == 200
    assert r.json() == {"recommendations_by_k": {"3": [1, 2, 3], "5": [1, 2, 3, 4, 5]}}

