def validate_credentials(username, password):
    if username == 'slot' and password == 'test':
        print('Valid credentials')
        return True
    else:
        print('Invalid credentials')
        return False