from app.models import Child
from app.models import Family
from app.models import User

"""
Generalized functions for use across the various routes defined in routes.py 
"""


class RouteUser:
    def define_active_user(self):
        self.user_family = self.return_user_family()
        self.user_children = self.return_user_children()
        self.user_active_child = self.return_user_active_child()
        self.user_active_child_name = self.return_user_active_child_name()

    def return_user_family(self):
        return Family.query.filter_by(user_id=self.active_user.get_id()).first()

    def return_user_children(self):
        return (
            None
            if self.user_family is None
            else Child.query.filter_by(family_id=self.user_family.id).all()
        )

    def return_user_active_child(self):
        return User.query.filter_by(id=self.active_user.get_id()).first().active_child

    def return_user_active_child_name(self):
        return (
            None
            if self.user_active_child is None
            else Child.query.filter_by(id=self.user_active_child)
            .first()
            .child_first_name
        )

    def __init__(self, current_user):
        self.active_user = current_user
        self.define_active_user()
