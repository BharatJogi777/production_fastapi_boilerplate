def validate_password_strength(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    if password.isalpha() or password.isdigit():
        raise ValueError("Password must contain letters and numbers")
    return password
