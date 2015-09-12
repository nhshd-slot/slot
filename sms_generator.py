def new_procedure_message(procedure, location, duration, doctor):
    unique_reference = str(1)
    message = str.format("{0} is available on {1}. Attend the ward in {2} and meet {3} in the junior doctors' office. "
                         "To accept this opportunity reply with {4}",
                         procedure,
                         ward,
                         duration,
                         doctor,
                         unique_reference)
    print(message)
    return message


def success_response_message(procedure, location, duration, doctor):
    message = str.format("Please attend {0} in {1} and ask for {2} to complete this supervised "
                         "procedure. This learning opportunity has been reserved exclusively for you, please make "
                         "every effort to attend.",
                         ward,
                         duration,
                         doctor)
    print(message)
    return message


def not_successful_response_message():
    message = str.format("Sorry - procedure already taken this time.")

    print(message)
    return message