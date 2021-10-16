from __future__ import annotations
from hikari import Permissions
from lightbulb import Context


def check_permission(context: Context, permission: Permissions, /):
    perms = [role.permissions.any(permission) for role in context.member.get_roles(
    ) if role.permissions.any(permission, Permissions.ADMINISTRATOR)]
    if len(perms) > 0 or context.get_guild().owner_id == context.author.id:
        return True
    return False
