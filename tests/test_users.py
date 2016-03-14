from context import slot_users_controller as uc
from context import User


class TestUsers:

    # def test_validate_credentials_returns_true_for_valid_credentials(self):
    #     result = uc.return_user_if_valid_credentials('slot', 'test')
    #     assert result is True
    #
    # def test_validate_credentials_returns_false_for_invalid_credentials(self):
    #     result = uc.return_user_if_valid_credentials('bad_username', 'bad_password')
    #     assert result is False

    def test_convert_dict_to_user_instance_returns_valid_user_instance(self):
        result = uc.convert_user_dict_to_user_instance({'username': 'slot', 'password': 'test'})
        assert isinstance(result, User)
        assert result.id == 'slot'
        assert result.password == 'test'