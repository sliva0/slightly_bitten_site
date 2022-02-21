from dataclasses import dataclass, field

import flask


@dataclass
class RequestPath:
    _path: list[str] = field(default_factory=list)
    is_not_found: bool = False

    @staticmethod
    def join_link(path: list[str]):
        return "/" + "/".join(path) if path else ""

    @property
    def breadcrumbs_links(self):
        current_path = []
        for name in self._path:
            current_path.append(name)
            yield name, self.join_link(current_path)

    @property
    def path(self):
        return self.join_link(self._path)

    @property
    def parent(self):
        return self.join_link(self._path[:-1])

    @property
    def page_name(self):
        return self._path[-1]

    def add(self, name):
        self._path.append(name)

    @staticmethod
    def set_request_path():
        flask.g.rpath = RequestPath()


def init(app: flask.Flask):
    app.before_request(RequestPath.set_request_path)