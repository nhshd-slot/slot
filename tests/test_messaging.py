from context import slot


class TestMessaging:

    def test_converts_mobile_string_to_int(self):
        result = slot.messaging.mobile_number_string_to_int("441234567890")
        assert isinstance(result, int)
        assert (result == 441234567890)

    def test_converts_mobile_int_to_int(self):
        result = slot.messaging.mobile_number_string_to_int(441234567890)
        assert isinstance(result, int)
        assert (result == 441234567890)
