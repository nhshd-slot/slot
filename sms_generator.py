def generate_new_procedure_message(procedure, ward, timeframe, doctor):
    unique_reference = str(1)
    message = str.format("{0} is available on {1}. Attend the ward in {2} and meet {3} in the junior doctors' office. "
                         "To accept this opportunity reply with {4}",
                         procedure,
                         ward,
                         timeframe,
                         doctor,
                         unique_reference)
    print(message)
    return message


def generate_success_response_message(procedure, ward, timeframe, doctor):
    message = str.format("Please attend {0} in {1} and ask for {2} to complete this supervised "
                         "procedure. This learning opportunity has been reserved exclusively for you, please make "
                         "every effort to attend.",
                         ward,
                         timeframe,
                         doctor)
    print(message)
    return message


def generate_not_success_response_message():
    message = str.format("Sorry - procedure already taken this time.")

    print(message)
    return message