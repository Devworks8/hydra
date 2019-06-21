import sys
from cmd2 import cmd2, with_argument_list
import cmd2_submenu


SETTINGS = None
BOT = None


class SettingsSM(cmd2.Cmd):
    """Local settings manipulation. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = 'Settings '
        self.top_level_attr = None
        self.settings_level_attr = 100000200

    def do_view(self, *args, **kwargs):
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


class PlayerSM(cmd2.Cmd):
    """Player controls."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = 'Player '
        self.top_level_attr = None
        self.player_level_attr = 100000300

    def do_play(self, *args, **kwargs):
        global BOT

        BOT.send_cmd([b'COMMAND', b'PLAY'], opt='player')

    def do_stop(self):
        pass

    def do_pause(self):
        pass

    def do_next(self):
        pass

    def do_prev(self):
        pass


@cmd2_submenu.AddSubmenu(SettingsSM(), command='settings', shared_attributes=dict(top_level_attr='hydra_level_attr'))
@cmd2_submenu.AddSubmenu(PlayerSM(), command='player', shared_attributes=dict(top_level_attr='hydra_level_attr'))
class CLIShell(cmd2.Cmd):
    """To be used as the main / top level command class that will contain other submenus."""

    def __init__(self, bot, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = 'Hydra >>'
        self.hydra_level_attr = 100000100
        global BOT
        BOT = bot
        global SETTINGS
        SETTINGS = settings

    def do_say(self, line):
        print("You called a command in TopLevel with '%s'. "
              "TopLevel has attribute top_level_attr=%s" % (line, self.top_level_attr))

    def help_say(self):
        print("This is a top level submenu. Options are settings, quit")

    def complete_say(self, text, line, begidx, endidx):
        return [s for s in ['settings', 'quit'] if s.startswith(text)]

