from app import app, db
from app.models import User, Family, Child, Feed


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Family": Family, "Child": Child, "Feed": Feed}
