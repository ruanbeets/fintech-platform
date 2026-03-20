# Placeholder until you add user_settings table

class SettingsViewModel:

    @staticmethod
    def get_settings(user_id: str):
        return {
            "theme": "light",
            "currency": "USD"
        }

    @staticmethod
    def update_settings(user_id: str, data: dict):
        # later: persist to DB
        return {
            "message": "Settings updated",
            "data": data
        }