from app.viewmodels.users_vm import UsersViewModel


class AuthViewModel:

    @staticmethod
    def register(data: dict):
        # hashing should happen here later
        return UsersViewModel.create_user(data)

    @staticmethod
    def login(data: dict):
        user = UsersViewModel.get_user_by_email(data["email"])

        if not user:
            return None

        # later: verify password hash
        if user.password_hash != data["password"]:
            return None

        return user