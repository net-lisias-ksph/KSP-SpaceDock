from flask import Blueprint, render_template, redirect, request, abort
from flask_login import login_user, current_user
from sqlalchemy import desc, or_

from ..common import adminrequired, with_session
from ..database import db
from ..email import send_bulk_email
from ..objects import Mod, GameVersion, Game, Publisher, User

admin = Blueprint('admin', __name__, template_folder='../../templates/admin')


@admin.route("/admin")
@adminrequired
def backend():
    users = User.query.count()
    usrs = User.query.order_by(desc(User.created))
    mods = Mod.query.count()
    versions = GameVersion.query.order_by(desc(GameVersion.id)).all()
    games = Game.query.filter(Game.active == True).order_by(desc(Game.id)).all()
    publishers = Publisher.query.order_by(desc(Publisher.id)).all()
    return render_template("admin.html", users=users, mods=mods, usrs=usrs, versions=versions, games=games, publishers=publishers)


@admin.route("/admin/impersonate/<username>")
@adminrequired
def impersonate(username):
    user = User.query.filter(User.username == username).first()
    login_user(user)
    return redirect("/")


@admin.route("/versions/create", methods=['POST'])
@adminrequired
@with_session
def create_version():
    friendly = request.form.get("friendly_version")
    gid = request.form.get("ganame")
    if not friendly or not gid:
        return redirect("/asdf")
    if any(GameVersion.query.filter(GameVersion.friendly_version == friendly)):
        return redirect("/fsda")
    version = GameVersion(friendly_version=friendly, game_id=gid)
    db.add(version)
    db.commit()
    return redirect("/admin")


@admin.route("/games/create", methods=['POST'])
@adminrequired
@with_session
def create_game():
    name = request.form.get("gname")
    sname = request.form.get("sname")
    pid = request.form.get("pname")
    if not name or not pid or not sname:
        return redirect("/asdf")
    if any(Game.query.filter(Game.name == name)):
        return redirect("/fsda")

    go = Game(name=name, publisher_id=pid, short=sname)
    db.add(go)
    db.commit()
    return redirect("/admin")


@admin.route("/publishers/create", methods=['POST'])
@adminrequired
@with_session
def create_publisher():
    name = request.form.get("pname")
    if not name:
        return redirect("/asdf")
    if any(Publisher.query.filter(Publisher.name == name)):
        return redirect("/fsda")
    gname = Publisher(name=name)
    db.add(gname)
    db.commit()
    return redirect("/admin")


@admin.route("/admin/email", methods=['POST'])
@adminrequired
def email():
    subject = request.form.get('subject')
    body = request.form.get('body')
    modders_only = request.form.get('modders-only') == 'on'
    if not subject or not body:
        abort(400)
    users = User.query
    if modders_only:
        users = db.query(User.email) \
            .filter(or_(User.username == current_user.username,
                        db.query(Mod.id).filter(Mod.user_id == User.id).exists()))
    send_bulk_email([u.email for u in users], subject, body)
    return redirect("/admin")


@admin.route("/admin/manual-confirmation/<int:user_id>")
@adminrequired
@with_session
def manual_confirm(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)
    user.confirmation = None
    return redirect("/profile/" + user.username)
