def test_token_validity(admin_token, user_token):
    assert isinstance(admin_token, str)
    assert isinstance(user_token, str)
    assert len(admin_token) > 10
    assert len(user_token) > 10
