from tatneft_back.core.enumerations import UserRoles


def roles_to_list(roles: UserRoles) -> list[str]:
    if isinstance(roles, str):
        roles = [roles]
    elif isinstance(roles, set):
        roles = list(roles)
    elif isinstance(roles, list):
        pass
    else:
        raise TypeError("bad type for roles")
    return roles
