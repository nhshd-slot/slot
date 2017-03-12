from context import slot


class TestMessaging:

    def test_converts_mobile_string_to_int(self):
        result = slot.messaging.mobile_number_string_to_int("441234567890")
        assert isinstance(result, int)
        assert (result == 441234567890)

    def test_converts_mobile_string_with_plus_prefix_to_int(self):
        result = slot.messaging.mobile_number_string_to_int("+441234567890")
        assert isinstance(result, int)
        assert (result == 441234567890)

    def test_converts_mobile_int_to_int(self):
        result = slot.messaging.mobile_number_string_to_int(441234567890)
        assert isinstance(result, int)
        assert (result == 441234567890)

    def test_list_is_shuffled(self):
        list = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6', 'item 7', 'item 8', 'item 9', ]
        result = slot.messaging.shuffle_list(list)
        result2 = slot.messaging.shuffle_list(list)
        print(list)
        print(result)
        print(result2)
        assert (list != result)
        assert(list != result2)
        assert (result != result2)