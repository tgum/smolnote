import os
from pathlib import Path
import time

import chevron

# import bcrypt

import minittp
from minittp import Response

import database

script_dir = os.path.dirname(__file__)  # Get the directory of the current script


def rel_file(path):
    return os.path.join(script_dir, path)


def unix_to_str(timestamp):
    return time.strftime("%Y/%m/%d %H:%M", time.gmtime(int(float(timestamp))))


templates = {}
for file in list(Path(script_dir).rglob("*.mustache")):
    with open(file) as f:
        path = (
            str(file)
            .removeprefix(script_dir)
            .removeprefix("/templates/")
            .removesuffix(".mustache")
        )
        templates[path] = f.read()
for key in templates:
    if key in ["page"]:
        continue
    templates[key] = chevron.render(templates["page"], {"content": templates[key]})


class Home(minittp.RequestHandler):
    def handler(self, req):
        user = 1
        res = Response()
        notes_obj = []
        msg = ""
        if "msg" in req.query:
            msg = req.query["msg"][0]
        notes = database.get_notes_by_user(user)
        for note in reversed(notes):
            with open(Path(f"users/{user}/notes/") / (note[2] + ".txt")) as f:
                next_note = {
                    "noteid": note[0],
                    "name": note[1],
                    "filename": note[2],
                    "creatorid": note[3],
                    "creation_date": unix_to_str(note[4]),
                    "modified": unix_to_str(note[5]),
                    "public": unix_to_str(note[6]),
                    "content": f.read(),
                }

                notes_obj.append(next_note)
        res.body = chevron.render(templates["home"], {"notes": notes_obj, "msg": msg})
        return res


class New(minittp.RequestHandler):
    def handler(self, req):
        user = 1
        res = Response()
        if "content" not in req.query:
            return False
        if "name" not in req.query:
            return False
        name = req.query["name"][0]
        content = req.query["content"][0]
        with open(Path(f"users/{user}/notes/") / (name + ".txt"), "w") as f:
            f.write(content)
            database.add_note(name, user)
        res.status = 303
        res.headers["Location"] = "/"
        return res


class DeleteConfirm(minittp.RequestHandler):
    def handler(self, req):
        res = Response()
        if "id" not in req.query:
            return False
        noteid = req.query["id"][0]
        note = database.get_note_by_id(noteid)
        res.body = chevron.render(
            templates["delete_confirm"], {"name": note[1], "id": noteid}
        )
        return res


class Delete(minittp.RequestHandler):
    def handler(self, req):
        user = 1
        res = Response()
        if "id" not in req.query:
            return False
        noteid = req.query["id"][0]
        note = database.get_note_by_id(noteid)
        if note[3] != user:
            res.body = "You cant delete someone elses notes..."
            return res
        database.delete_note(noteid)
        notepath = Path(f"users/{user}/notes/") / (note[2] + ".txt")
        notepath.unlink()
        res.status = 303
        res.headers["Location"] = "/"
        return res


class Edit(minittp.RequestHandler):
    def handler(self, req):
        user = 1
        res = Response()
        if "id" not in req.query:
            return False
        noteid = req.query["id"][0]
        note = database.get_note_by_id(noteid)
        if note[3] != user:
            res.body = "You cant edit some other dudes notes like that lol"
            return res

        with open(Path(f"users/{user}/notes/") / (note[2] + ".txt")) as f:
            content = f.read()

        res.body = chevron.render(
            templates["edit"], {"id": noteid, "name": note[1], "content": content}
        )
        return res


class SaveEdit(minittp.RequestHandler):
    def handler(self, req):
        user = 1
        res = Response()
        if "id" not in req.query:
            return False
        if "name" not in req.query:
            return False
        if "content" not in req.query:
            return False
        noteid = req.query["id"][0]
        new_name = req.query["name"][0]
        new_content = req.query["content"][0]
        note = database.get_note_by_id(noteid)
        if note[3] != user:
            res.body = "You cant edit some other dudes notes like that lol"
            return res
        database.set_note_name(noteid, new_name)
        with open(Path(f"users/{user}/notes/") / (note[2] + ".txt"), "w") as f:
            f.write(new_content)
        res.status = 303
        res.headers["Location"] = "/"
        return res


if __name__ == "__main__":
    server = minittp.Server("", 8080)
    server.register_handler(r"/(\?.*)?", Home())
    server.register_handler(r"/new(\?.*)?", New())
    server.register_handler(r"/delete_confirm(\?.*)?", DeleteConfirm())
    server.register_handler(r"/delete(\?.*)?", Delete())
    server.register_handler(r"/edit(\?.*)?", Edit())
    server.register_handler(r"/save_edit(\?.*)?", SaveEdit())
    server.start()
