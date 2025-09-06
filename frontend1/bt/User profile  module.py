class User:
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_profile(self, username=None, email=None, password=None):
        if username: self.username = username
        if email: self.email = email
        if password: self.password_hash = generate_password_hash(password)