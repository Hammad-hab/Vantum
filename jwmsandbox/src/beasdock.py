#!/usr/bin/env python3

import gi
import os

if os.environ.get("WAYLAND_DISPLAY"):
    os.environ["GDK_BACKEND"] = "x11"
    os.environ["DISPLAY"] = ":1"

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

try:
    from Xlib import display as xdisplay, X
    from Xlib.protocol import event as xevent
    _xdisp = xdisplay.Display()
    _root  = _xdisp.screen().root
    HAVE_XLIB = True
except ImportError:
    HAVE_XLIB = False

DOCK_H    = 52
POLL_MS   = 900
OWN_TITLE = "BeasDock"

CSS = """
window#beasdock { background: transparent; }

#bar {
    background-color: rgba(20, 20, 28, 0.90);
    border: 1px solid rgba(255,255,255,0.10);
    padding: 4px 10px;
}

#bar button {
    background: transparent;
    border: none;
    outline: none;
    box-shadow: none;
    padding: 4px 10px;
    min-height: 38px;
    color: #dddddd;
    font-size: 13px;
}

#bar button:focus    { outline: none; box-shadow: none; border: none; }
#bar button:hover    { background-color: rgba(255,255,255,0.14); }
#bar button:active   { background-color: rgba(255,255,255,0.22); }
#bar button:backdrop { background: transparent; color: #dddddd; opacity: 1; }
#bar button:disabled { background: transparent; color: #dddddd; opacity: 1; }
*:backdrop           { opacity: 1; }
"""

# ── Xlib helpers ──────────────────────────────────────────────────────────────

def _atom(name):
    return _xdisp.intern_atom(name)

def _prop(win, atom):
    try:
        r = win.get_full_property(atom, X.AnyPropertyType)
        return r.value if r else None
    except Exception:
        return None

def _text(win, atom):
    try:
        r = win.get_full_property(atom, X.AnyPropertyType)
        if r is None:
            return None
        v = r.value
        if isinstance(v, (bytes, bytearray)):
            return v.decode("utf-8", errors="replace").rstrip("\x00")
        return str(v)
    except Exception:
        return None

def list_windows():
    if not HAVE_XLIB:
        return []
    wins = []
    try:
        client_list = _prop(_root, _atom("_NET_CLIENT_LIST"))
        if client_list is None:
            return []
        a_name   = _atom("_NET_WM_NAME")
        a_state  = _atom("_NET_WM_STATE")
        a_skip   = _atom("_NET_WM_STATE_SKIP_TASKBAR")
        a_wtype  = _atom("_NET_WM_WINDOW_TYPE")
        a_normal = _atom("_NET_WM_WINDOW_TYPE_NORMAL")
        a_dialog = _atom("_NET_WM_WINDOW_TYPE_DIALOG")
        for wid in client_list:
            try:
                win = _xdisp.create_resource_object("window", wid)
                state = _prop(win, a_state)
                if state and a_skip in state:
                    continue
                wtype = _prop(win, a_wtype)
                if wtype is not None and a_normal not in wtype and a_dialog not in wtype:
                    continue
                title = _text(win, a_name) or _text(win, _atom("WM_NAME")) or "?"
                if title == OWN_TITLE or not title.strip():
                    continue
                wins.append((wid, title))
            except Exception:
                continue
    except Exception:
        pass
    return wins

def activate_window(wid):
    if not HAVE_XLIB:
        return
    try:
        win = _xdisp.create_resource_object("window", wid)
        ev  = xevent.ClientMessage(
            window=win,
            client_type=_atom("_NET_ACTIVE_WINDOW"),
            data=(32, [2, X.CurrentTime, 0, 0, 0]),
        )
        _root.send_event(ev, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        _xdisp.flush()
    except Exception:
        pass

# ── Dock ──────────────────────────────────────────────────────────────────────

class BeasDock(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_name("beasdock")
        self.set_title(OWN_TITLE)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.stick()

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        prov = Gtk.CssProvider()
        prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            screen, prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._geo = screen.get_monitor_geometry(screen.get_primary_monitor())

        outer = Gtk.Box()
        outer.set_halign(Gtk.Align.CENTER)
        outer.set_valign(Gtk.Align.CENTER)
        self._bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self._bar.set_name("bar")
        outer.add(self._bar)
        self.add(outer)

        # Track current buttons as {wid: (title, Gtk.Button)}
        self._buttons = {}
        # Track current ordered list of wids so we can detect reorders
        self._order = []

        self.show_all()
        self._refresh()
        GLib.timeout_add(POLL_MS, self._refresh)

    def do_draw(self, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        Gtk.Window.do_draw(self, cr)

    def _place(self):
        geo = self._geo
        w = min(self.get_preferred_size()[1].width, geo.width - 40)
        self.resize(w, DOCK_H)
        self.move(geo.x + (geo.width - w) // 2,
                  geo.y + geo.height - DOCK_H - 20)

    def _make_button(self, wid, title):
        short = title if len(title) <= 28 else title[:26] + "…"
        btn = Gtk.Button(label=short)
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.set_focus_on_click(False)
        btn.set_tooltip_text(title)
        btn.connect("clicked", lambda _b, w=wid: activate_window(w))
        btn.show()
        return btn

    def _refresh(self):
        wins = list_windows()  # [(wid, title), ...]
        new_wids = [wid for wid, _ in wins]
        new_titles = {wid: title for wid, title in wins}

        # Remove buttons for closed windows
        gone = [wid for wid in self._buttons if wid not in new_titles]
        for wid in gone:
            _, btn = self._buttons.pop(wid)
            self._bar.remove(btn)
            btn.destroy()

        # Add buttons for new windows
        for wid, title in wins:
            if wid not in self._buttons:
                btn = self._make_button(wid, title)
                self._buttons[wid] = (title, btn)
                self._bar.pack_start(btn, False, False, 0)
            else:
                old_title, btn = self._buttons[wid]
                # Update label if title changed (e.g. browser tab switch)
                if old_title != title:
                    short = title if len(title) <= 28 else title[:26] + "…"
                    btn.set_label(short)
                    btn.set_tooltip_text(title)
                    self._buttons[wid] = (title, btn)

        # Reorder bar children to match window list order
        if new_wids != self._order:
            for i, wid in enumerate(new_wids):
                _, btn = self._buttons[wid]
                self._bar.reorder_child(btn, i)
            self._order = new_wids

        # No-windows placeholder
        placeholders = [c for c in self._bar.get_children()
                        if isinstance(c, Gtk.Label)]
        if not wins and not placeholders:
            lbl = Gtk.Label(label="No windows open" if HAVE_XLIB else "Install python3-xlib")
            lbl.set_margin_start(14)
            lbl.set_margin_end(14)
            lbl.show()
            self._bar.pack_start(lbl, False, False, 0)
        elif wins:
            for c in placeholders:
                self._bar.remove(c)
                c.destroy()

        GLib.idle_add(self._place)
        return True


def main():
    if not HAVE_XLIB:
        print("python3-xlib is required:  sudo apt install python3-xlib")
    dock = BeasDock()
    dock.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()