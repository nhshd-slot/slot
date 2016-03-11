def return_user_if_valid_credentials(username, password):
    # Try and retrieve the user from the database using the username - if successful it means the user exists
    user = db.get_user(username)

    if user:
        # Check that the password is correct
        if password == user['password']:
            print('Valid credentials')
            user_instance = return_user_instance_or_anonymous(user)
            if isinstance(user_instance, models.User):
                return user_instance

    else:
        print('Invalid credentials')
        return None
