from app import app, db
from app.models import User, Parent, Child, Feed


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Parent": Parent, "Child": Child, "Feed": Feed}
