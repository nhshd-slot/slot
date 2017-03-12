from context import slot


class TestSMSCreator:

    def test_new_procedure_message(self):
        procedure = "Dressing"
        location = "Ward 999"
        expiry_time = "14:00"
        doctor = "Dr Testing"
        message_ref = 24
        message = slot.sms_creator.new_procedure_message(procedure, location, expiry_time, doctor, message_ref)
        print(message)
        assert (message == "Dressing at Ward 999.\nAttend by 14:00.\nAsk for Dr Testing.\n\nTo accept reply '24'")
