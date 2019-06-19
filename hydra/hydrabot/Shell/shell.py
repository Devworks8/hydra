import sys
from cmd2 import cmd2, with_argument_list
import cmd2_submenu
from IPython import embed


SETTINGS = None


class SettingsSM(cmd2.Cmd):
    """Local settings manipulation. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = 'Settings '
        self.top_level_attr = None
        self.settings_level_attr = 100000200

    def do_view(self, args):
        global SETTINGS
        print(SETTINGS.show_config())

    @with_argument_list
    def do_set(self, arglist):
        global SETTINGS
        SETTINGS.set(arglist[0], arglist[1])
        print("set {} {}: Operation successfully completed.".format(arglist[0], arglist[1]))

    def do_save(self):
        global SETTINGS
        SETTINGS.save()
        print("Save: Operation successfully completed.")


@cmd2_submenu.AddSubmenu(SettingsSM(), command='settings', shared_attributes=dict(top_level_attr='hydra_level_attr'))
class CLIShell(cmd2.Cmd):
    """To be used as the main / top level command class that will contain other submenus."""

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = 'Hydra >>'
        self.hydra_level_attr = 100000100
        global SETTINGS
        SETTINGS = settings

    def do_ipy(self, arg):
        """Enters an interactive IPython shell.
        Run python code from external files with ``run filename.py``
        End with ``Ctrl-D`` (Unix) / ``Ctrl-Z`` (Windows), ``quit()``, '`exit()``.
        """
        banner = 'Entering an embedded IPython shell type quit() or <Ctrl>-d to exit ...'
        exit_msg = 'Leaving IPython, back to {}'.format(sys.argv[0])
        embed(banner1=banner, exit_msg=exit_msg)

    def do_say(self, line):
        print("You called a command in TopLevel with '%s'. "
              "TopLevel has attribute top_level_attr=%s" % (line, self.top_level_attr))

    def help_say(self):
        print("This is a top level submenu. Options are qwe, asd, zxc")

    def complete_say(self, text, line, begidx, endidx):
        return [s for s in ['qwe', 'asd', 'zxc'] if s.startswith(text)]
