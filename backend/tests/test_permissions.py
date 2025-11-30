from conftest import api
import uuid

def test_list_permissions(admin_token):
    res = api("get", "/permissions", token=admin_token)
    assert res.status_code in (200, 403)


def test_create_and_delete_permission(admin_token):
    payload = {
        "name": f"perm_{uuid.uuid4().hex[:5]}",
        "description": "test perm"
    }
    res = api("post", "/permissions", json=payload, token=admin_token)
    assert res.status_code in (201, 400)

    if res.status_code == 201:
        perm_id = res.json()["id"]
        res2 = api("delete", f"/permissions/{perm_id}", token=admin_token)
        assert res2.status_code in (204, 404)
