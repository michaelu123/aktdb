from .models import Member


def is_admin(req):
    user = req.user
    if user.is_superuser:
        return True
    grps = list(user.groups.all())
    for grp in grps:
        if grp.name == "admins":
            return True
    return False


def getMySelfId(req):
    myselfId = req.session.get("myselfId")
    if myselfId == None:
        user = req.user
        myself = Member.objects.get(
            first_name=user.first_name, last_name=user.last_name)
        req.session["myselfId"] = myself.id
    return myselfId
