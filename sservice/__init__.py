import logging

import sh
from sh import ErrorReturnCode


class SService(object):

    COMMANDS = [
        "daemon_reload",
        "disable",
        "enable",
        "is_installed",
        "is_active",
        "reload",
        "restart",
        "start",
        "status",
        "stop",
    ]

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger("sservice.%s" % (name))
        self._instance = None
        self._with_service_name = True

    def __getattr__(self, command):
        if command not in self.COMMANDS:
            return super(SService, self).__getattr__(command)
        elif command == "is_installed":
            def is_installed(bg=False):
                try:
                    sh.grep(
                        sh.systemctl(
                            "--no-page",
                            "list-unit-files",
                            _bg=bg,
                            _piped=True),
                        self.name)
                    return True
                except Exception:
                    return False
            return is_installed
        elif command == "is_active":
            def is_active(bg=False):
                try:
                    sh.systemctl(
                        "--no-page",
                        "is-active",
                        self.name,
                        _bg=bg)
                    return True
                except ErrorReturnCode:
                    return False
            return is_active
        elif command in ["daemon_reload"]:
            self._with_service_name = False
            args = ["daemon-reload"]
        elif command in [
                "disable", "enable", "reload", "restart",
                "start", "status", "stop"]:
            self._with_service_name = True
            args = [
                "--no-page",
                command]

        def do_command(bg=False, instance=None):
            if instance:
                self._instance = instance
            _name = "{}".format(self.name)
            if self._instance:
                _name = _name + self._instance
            if self._with_service_name:
                args.append(_name)

            try:
                output = sh.systemctl(
                    args, _bg=bg, _no_out=True)
                self.logger.debug(
                    "SService '%s' %s" % (self.name, command))
                return output.exit_code
            except ErrorReturnCode as e:
                self.logger.debug(
                    "SService '%s' %s failed" %
                    (self.name, command))
                self.logger.debug(str(e))
                return e.exit_code

        return do_command
