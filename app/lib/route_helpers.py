from app.models import Child
from app.models import Family
from app.models import User

from datetime import datetime

"""
Generalized functions for use across the various routes defined in routes.py 
"""


class RouteUser:
    def define_active_user(self):
        self.user_family = self.return_user_family()
        self.user_children = self.return_user_children()
        self.user_active_child = self.return_user_active_child()
        self.user_active_child_name = self.return_user_active_child_name()
        self.user_ordered_child_list = self.return_ordered_child_list()

    def return_user_family(self):
        return Family.query.filter_by(user_id=self.active_user.get_id()).first()

    def return_user_children(self):
        return (
            None
            if self.user_family is None
            else Child.query.filter_by(family_id=self.user_family.id).all()
        )

    # TODO: Determine if this ordering is still relevent
    def return_ordered_child_list(self):
        if self.user_children is not None:
            user_children_list = [
                (c.id, c.child_first_name) for c in self.user_children
            ]
            for c in user_children_list:
                if c[0] == self.user_active_child:
                    user_children_list.insert(0, user_children_list.pop())

            return user_children_list
        else:
            return None

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


def return_current_date_string():
    return datetime.now().strftime("%A, %B %d %Y")
