import .app.slot.messaging


class TestMessaging:

    def test_converts_mobile_string_to_int(self):
        result = app.slot.messaging.mobile_number_string_to_int("441234567890")
        assert isinstance(result, int)
        assert (result == 441234567890)
