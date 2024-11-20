import os

import chevron

import minittp
from minittp import Response


def relative_file(path):
    script_dir = os.path.dirname(__file__)  # Get the directory of the current script
    return os.path.join(script_dir, path)


class Home(minittp.RequestHandler):
    def handler(self, req):
        res = Response()
        with open("templates/home.mustache") as f:
            res.body = chevron.render(f.read(), {"title": "HOme", "body": "hey dood"})
        return res


if __name__ == "__main__":
    server = minittp.Server("", 8080)
    server.register_handler(r"/index.html", Home())
    server.internal_redirect(r"/(.*/)?", r"/\1index.html")
    server.start()
