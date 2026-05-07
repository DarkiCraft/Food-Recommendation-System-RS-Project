## Manual testing guide (Munchify-Backend)

This guide is a practical end-to-end checklist you can run against a locally running API.

### Prerequisites
- Postgres running and a valid `DATABASE_URL`
- Create a `.env` based on `.env.example`
- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Start the server

```bash
uvicorn main:app --reload
```

The API will be at `http://127.0.0.1:8000`.

### 1) Auth (Signup + Login)

Signup:

```bash
curl -X POST "http://127.0.0.1:8000/auth/signup" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_name\":\"alice\",\"email\":\"alice@example.com\",\"password\":\"Password123\"}"
```

Login:

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=alice@example.com&password=Password123"
```

Copy the `access_token` from the response and set:

- `TOKEN=<access_token>`

### 2) Admin API key auth

Set:
- `ADMIN_TOKEN=<ADMIN_API_KEY from .env>`

Check stats (requires admin header):

```bash
curl "http://127.0.0.1:8000/admin/stats" ^
  -H "X-Admin-Token: %ADMIN_TOKEN%"
```

### 3) Admin item create/delete

Create an item:

```bash
curl -X POST "http://127.0.0.1:8000/admin/items" ^
  -H "Content-Type: application/json" ^
  -H "X-Admin-Token: %ADMIN_TOKEN%" ^
  -d "{\"item_name\":\"Spicy Ramen\",\"cuisine\":\"Japanese\"}"
```

Copy returned `item_id` and set:
- `ITEM_ID=<item_id>`

Delete:

```bash
curl -X DELETE "http://127.0.0.1:8000/admin/items/%ITEM_ID%" ^
  -H "X-Admin-Token: %ADMIN_TOKEN%"
```

### 4) Activity endpoints (JWT required)

Click:

```bash
curl -X POST "http://127.0.0.1:8000/activity/click" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"item_id\":%ITEM_ID%}"
```

Order (returns `order_id`):

```bash
curl -X POST "http://127.0.0.1:8000/activity/order" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"item_id\":%ITEM_ID%}"
```

Set:
- `ORDER_ID=<order_id>`

Rate:

```bash
curl -X POST "http://127.0.0.1:8000/activity/rate" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"order_id\":%ORDER_ID%,\"rating\":5}"
```

### 5) Recommendations

Single `k`:

```bash
curl "http://127.0.0.1:8000/recommendations?k=5" ^
  -H "Authorization: Bearer %TOKEN%"
```

Multiple `k` values:

```bash
curl "http://127.0.0.1:8000/recommendations?k=3&k=5" ^
  -H "Authorization: Bearer %TOKEN%"
```

Expected response shape:
- single `k`: `{ "recommendations": [...] }`
- multi `k`: `{ "recommendations_by_k": { "3":[...], "5":[...] } }`

### 6) Re-train recommender (admin)

```bash
curl -X POST "http://127.0.0.1:8000/admin/retrain" ^
  -H "X-Admin-Token: %ADMIN_TOKEN%"
```

Notes:
- This can take time depending on dataset size and `EPOCHS`.
- The NCF model artifact is stored at `artifacts/ncf_model.pth`.

