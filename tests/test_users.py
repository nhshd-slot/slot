from context import slot_users_controller as uc


class TestUsers:

    def test_validate_credentials_returns_true_for_valid_credentials(self):
        result = uc.return_user_if_valid_credentials('slot', 'test')
        assert result is True

    def test_validate_credentials_returns_false_for_invalid_credentials(self):
        result = uc.return_user_if_valid_credentials('bad_username', 'bad_password')
        assert result is False

    def test_convert_dict_to_user_instance_returns_valid_user_instance(self):
        result = uc.convert_dict_to_user_instance({})
        assert result