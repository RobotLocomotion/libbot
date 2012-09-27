import cStringIO as StringIO
import traceback

import gobject
import gtk

from bot_procman.sheriff_config import Parser, ScriptNode
from bot_procman.sheriff_script import SheriffScript

class AddModifyCommandDialog (gtk.Dialog):
    def __init__ (self, parent, deputies, groups,
            initial_cmd="", initial_nickname="", initial_deputy="",
            initial_group="", initial_auto_respawn=False):
        # add command dialog
        gtk.Dialog.__init__ (self, "Add/Modify Command", parent,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        table = gtk.Table(5, 2)

        # deputy
        table.attach (gtk.Label ("Deputy"), 0, 1, 0, 1, 0, 0)
        self.host_cb = gtk.combo_box_new_text()

        dep_ind = 0
        deputies.sort ()
        for deputy in deputies:
            self.host_cb.append_text (deputy)
            if deputy == initial_deputy:
                self.host_cb.set_active (dep_ind)
            dep_ind += 1
        if self.host_cb.get_active () < 0 and len(deputies) > 0:
            self.host_cb.set_active (0)

        table.attach (self.host_cb, 1, 2, 0, 1)
        self.deputies = deputies

        # command name
        table.attach (gtk.Label ("Command"), 0, 1, 1, 2, 0, 0)
        self.name_te = gtk.Entry ()
        self.name_te.set_text (initial_cmd)
        self.name_te.set_width_chars (60)
        table.attach (self.name_te, 1, 2, 1, 2)
        self.name_te.connect ("activate",
                lambda e: self.response (gtk.RESPONSE_ACCEPT))
        self.name_te.grab_focus ()

        # command nickname
        table.attach (gtk.Label ("Name"), 0, 1, 2, 3, 0, 0)
        self.nickname_te = gtk.Entry ()
        self.nickname_te.set_text (initial_nickname)
        self.nickname_te.set_width_chars (60)
        table.attach (self.nickname_te, 1, 2, 2, 3)
        self.nickname_te.connect ("activate",
                lambda e: self.response (gtk.RESPONSE_ACCEPT))

        # group
        table.attach (gtk.Label ("Group"), 0, 1, 3, 4, 0, 0)
        self.group_cbe = gtk.combo_box_entry_new_text ()
#        groups = groups[:]
        groups.sort ()
        for group_name in groups:
            self.group_cbe.append_text (group_name)
        table.attach (self.group_cbe, 1, 2, 3, 4)
        self.group_cbe.child.set_text (initial_group)
        self.group_cbe.child.connect ("activate",
                lambda e: self.response (gtk.RESPONSE_ACCEPT))

        # auto respawn
        table.attach (gtk.Label ("Auto-restart"), 0, 1, 4, 5, 0, 0)
        self.auto_respawn_cb = gtk.CheckButton ()
        self.auto_respawn_cb.set_active (initial_auto_respawn)
        if (initial_auto_respawn<0):
            self.auto_respawn_cb.set_inconsistent(True);
        self.auto_respawn_cb.connect("toggled", self.auto_respawn_cb_callback)
        table.attach (self.auto_respawn_cb, 1, 2, 4, 5)

        self.vbox.pack_start (table, False, False, 0)
        table.show_all ()
    def auto_respawn_cb_callback(self, widget, data=None):
        if widget.get_inconsistent():
            widget.set_inconsistent(False)

    def get_deputy (self):
        model = self.host_cb.get_model()
        active = self.host_cb.get_active ()
        if active < 0: return None
        return model[active][0]

    def get_command (self): return self.name_te.get_text ()
    def get_nickname (self): return self.nickname_te.get_text ()
    def get_group (self): return self.group_cbe.child.get_text ()
    def get_auto_respawn (self):
        if self.auto_respawn_cb.get_inconsistent():
            return -1
        else:
             return self.auto_respawn_cb.get_active ()

class PreferencesDialog(gtk.Dialog):
    def __init__ (self, sheriff_gtk, parent):
        # add command dialog
        gtk.Dialog.__init__ (self, "Preferences", parent,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        table = gtk.Table(4, 2)

        # console rate limit
        table.attach(gtk.Label("Console rate limit (kB/s)"), 0, 1, 0, 1, 0, 0)
        self.rate_limit_sb = gtk.SpinButton()
        self.rate_limit_sb.set_digits(0)
        self.rate_limit_sb.set_increments(1, 1000)
        self.rate_limit_sb.set_range(0, 999999)
        self.rate_limit_sb.set_value(sheriff_gtk.cmd_console.get_output_rate_limit())

        table.attach(self.rate_limit_sb, 1, 2, 0, 1)

        # background color
        table.attach(gtk.Label("Console background color"), 0, 1, 1, 2, 0, 0)
        self.bg_color_bt = gtk.ColorButton(sheriff_gtk.cmd_console.get_background_color())
        table.attach(self.bg_color_bt, 1, 2, 1, 2)

        # foreground color
        table.attach(gtk.Label("Console text color"), 0, 1, 2, 3, 0, 0)
        self.text_color_bt = gtk.ColorButton(sheriff_gtk.cmd_console.get_text_color())
        table.attach(self.text_color_bt, 1, 2, 2, 3)

        # font
        table.attach(gtk.Label("Console font"), 0, 1, 3, 4, 0, 0)
        self.font_bt = gtk.FontButton(sheriff_gtk.cmd_console.get_font())
        table.attach(self.font_bt, 1, 2, 3, 4)

        self.vbox.pack_start (table, False, False, 0)
        table.show_all ()

def do_add_command_dialog(sheriff, cmds_ts, window):
    deputies = sheriff.get_deputies ()
    if not deputies:
        msgdlg = gtk.MessageDialog (window,
                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                "Can't add a command without an active deputy")
        msgdlg.run ()
        msgdlg.destroy ()
        return
    deputy_names = [deputy.name for deputy in deputies ]
    dlg = AddModifyCommandDialog (window, deputy_names,
            cmds_ts.get_known_group_names ())
    while dlg.run () == gtk.RESPONSE_ACCEPT:
        cmd = dlg.get_command ()
        cmd_nickname = dlg.get_nickname()
        deputy_name = dlg.get_deputy ()
        group = dlg.get_group ().strip ()
        auto_respawn = dlg.get_auto_respawn ()
        if not cmd.strip ():
            msgdlg = gtk.MessageDialog (window,
                    gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Invalid command")
            msgdlg.run ()
            msgdlg.destroy ()
        elif not deputy:
            msgdlg = gtk.MessageDialog (window,
                    gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Invalid deputy")
            msgdlg.run ()
            msgdlg.destroy ()
        else:
            sheriff.add_command (deputy_name, cmd, cmd_nickname, group, auto_respawn)
            break
    dlg.destroy ()

class AddModifyScriptDialog (gtk.Dialog):
    def __init__ (self, parent, script):
        # add command dialog
        title = "Edit script"
        if script is None:
            title = "New script"
        gtk.Dialog.__init__ (self, title, parent,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                 gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        self.set_default_size(800, 400)

        hbox = gtk.HBox()

        default_contents = 'script "script-name" {\n' \
                           '    # script commands here\n' \
                           '}'

        # script contents
        self.script_tv = gtk.TextView ()
        self.script_tv.set_editable(True)
        self.script_tv.set_accepts_tab(False)
        if script is not None:
            self.script_tv.get_buffer().set_text(str(script))
        else:
            self.script_tv.get_buffer().set_text(default_contents)
        sw = gtk.ScrolledWindow()
        sw.add(self.script_tv)
        hbox.pack_start(sw, True, True)
        if script is not None:
            self.script_tv.grab_focus()

#        # Help text
        help_tv = gtk.TextView()
        help_tv.set_editable(False)
        help_tv.set_sensitive(False)
        help_tv.get_buffer().set_text("""
    Example commands:
        start cmd "server" wait "running";
        start cmd "client";
        stop cmd "server" wait "stopped";
        restart group "mygroup";
        wait group "mygroup" status "running";
        wait ms 500;
        run_script "other-script-name";
""")

#    Refer to commands and groups by what appears in the Name column.
#    Valid actions are:
#        start|stop|restart cmd|group "nickname" [wait "running"|"stopped"];
#        wait ms ###;
#        run_script "other-script-name";

        hbox.pack_start(help_tv, False, False)
        self.vbox.pack_start(hbox, True, True)
        hbox.show_all()

#    def get_script_name (self): return self.name_te.get_text ()
    def get_script_contents (self):
        buf = self.script_tv.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter())

def _do_err_dialog(window, msg):
    msgdlg = gtk.MessageDialog (window,
            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
    msgdlg.set_markup("<span font_family=\"monospace\">%s</span>" % msg)
    msgdlg.run ()
    msgdlg.destroy ()

def _parse_script(sheriff, window, dlg):
    contents = dlg.get_script_contents()

    # check script for errors
    parser = Parser()
    try:
        cfg_node = parser.parse(StringIO.StringIO(contents))
    except ValueError, xcp:
#        traceback.print_exc()
        _do_err_dialog(window, str(xcp))
        return None

    script_nodes = cfg_node.scripts.values()
    if not script_nodes:
        _do_err_dialog(window, "That's not a script...")
        return None

    if len(script_nodes) > 1:
        _do_err_dialog(window, "Only one script {} stanza allowed!")
        return None

    script = SheriffScript.from_script_node(script_nodes[0])

    errors = sheriff.check_script_for_errors(script)
    if errors:
        print errors
        _do_err_dialog(window, "Script error.\n\n" + "\n   ".join(errors))
        return None
    return script

def do_add_script_dialog(sheriff, window):
    dlg = AddModifyScriptDialog (window, None)
    while dlg.run() == gtk.RESPONSE_ACCEPT:
        script = _parse_script(sheriff, window, dlg)
        if script is None:
            dlg.script_tv.grab_focus()
            continue
        if sheriff.get_script(script.name) is not None:
            _do_err_dialog(window,
                    "A script named %s already exists!" % script.name)
            continue
        sheriff.add_script(script)
        break
    dlg.destroy ()

def do_edit_script_dialog(sheriff, window, script):
    if sheriff.get_active_script():
        _do_err_dialog("Script editing is not allowed while a script is running.")
        return

    dlg = AddModifyScriptDialog (window, script)
    while dlg.run() == gtk.RESPONSE_ACCEPT:
        new_script = _parse_script(sheriff, window, dlg)
        if new_script is None:
            dlg.script_tv.grab_focus()
            continue
        if new_script.name != script.name:
            if sheriff.get_script(new_script.name) is not None:
                _do_err_dialog(window,
                        "A script named %s already exists!" % script.name)
                dlg.script_tv.grab_focus()
                continue
        sheriff.remove_script(script)
        sheriff.add_script(new_script)
        break
    dlg.destroy ()

def do_preferences_dialog(sheriff_gtk, window):
    dlg = PreferencesDialog(sheriff_gtk, window)

    if dlg.run() == gtk.RESPONSE_ACCEPT:
        sheriff_gtk.cmd_console.set_background_color(dlg.bg_color_bt.get_color())
        sheriff_gtk.cmd_console.set_text_color(dlg.text_color_bt.get_color())
        sheriff_gtk.cmd_console.set_output_rate_limit(dlg.rate_limit_sb.get_value_as_int())
        sheriff_gtk.cmd_console.set_font(dlg.font_bt.get_font_name())

#        sheriff_gtk.cmds_tv.set_background_color(dlg.bg_color_bt.get_color())
#        sheriff_gtk.cmds_tv.set_text_color(dlg.text_color_bt.get_color())
#
#        sheriff_gtk.hosts_tv.set_background_color(dlg.bg_color_bt.get_color())
#        sheriff_gtk.hosts_tv.set_text_color(dlg.text_color_bt.get_color())

    dlg.destroy()
