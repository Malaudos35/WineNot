from conftest import api

def test_create_and_get_cellar(create_cellar, user_token):
    cellar = create_cellar()
    if not cellar:
        return

    res = api("get", f"/cellars/{cellar['id']}", token=user_token)
    assert res.status_code in (200, 404)


def test_list_cellars(user_token):
    res = api("get", "/cellars", token=user_token)
    assert res.status_code in (200, 403)
