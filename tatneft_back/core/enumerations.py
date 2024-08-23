from tatneft_back.utils.enumeration import Enumeration


class UserRoles(Enumeration):
    user = "user"
    subscribed_user = "subscribed_user"
    dev = "dev"

    def set():
        return {"user", "subscribed_user", "dev"}


class MailCodeTypes(Enumeration):
    reg = "reg"
    auth = "auth"