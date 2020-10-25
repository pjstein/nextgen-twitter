# nextgen/events.py

from copy import deepcopy as clone
from datetime import datetime
from json import dumps


class Events(object):
    def __init__(self, *args, **kwargs):
        return

    def log(self, **kwargs):
        raise NotImplementedError(
            f"'log' is not implemented on {self.__class__.__name__}"
        )

    def create_event(self, **kwargs):
        cp = clone(kwargs)
        cp.update({"timestamp": datetime.utcnow().isoformat()})
        return cp


class EventLog(Events):
    def __init__(self, filepath, *args, **kwargs):
        super(EventLog, self).__init__(*args, **kwargs)
        self.filepath = filepath

    def log(self, action_type="UNKNOWN", **kwargs):
        # Not efficient, doesn't much matter.
        with open(self.filepath, "a") as f:
            f.write(f"{dumps(self.create_event(action_type=action_type, **kwargs))}\n")
