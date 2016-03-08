import slot.users.controller as uc


class TestUsers:

    def test_validate_credentials_returns_true_for_valid_credentials(self):
        result = uc.validate_credentials('slot', 'test')
        assert result is True

    def test_validate_credentials_returns_false_for_invalid_credentials(self):
        result = uc.validate_credentials('bad_username', 'bad_password')
        assert result is False