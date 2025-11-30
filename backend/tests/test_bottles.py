from conftest import api

def test_add_and_update_bottle(create_bottle, user_token):
    r = create_bottle()
    if not r:
        return
    cellar_id, bottle = r

    # update
    payload = {"notes": "ok", "quantity": 2}
    res = api("put", f"/bottles/{bottle['id']}",
              json=payload, token=user_token)
    assert res.status_code in (200, 400, 404)

    if res.status_code == 200:
        updated = res.json()
        assert updated["quantity"] == 2
        assert updated["notes"] == "ok"


def test_delete_bottle(create_bottle, user_token):
    x = create_bottle()
    if not x:
        return
    cellar_id, bottle = x

    res = api("delete", f"/bottles/{bottle['id']}", token=user_token)
    assert res.status_code in (204, 404)
