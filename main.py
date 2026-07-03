import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import random
import tracker
from file_handler import (register_user, verify_user,
                          load_activity, log_activity, set_current_user)

# ══════════════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════════════
BG         = "#080b14"
BG_CARD    = "#0e1320"
BG_INPUT   = "#151b2e"
BG_HOVER   = "#1a2238"
ACCENT     = "#00d4ff"
ACCENT2    = "#7b2fff"
GOLD       = "#ffd166"
SUCCESS    = "#06d6a0"
DANGER     = "#ef476f"
WARNING    = "#ffd166"
TEXT       = "#e8f4fd"
TEXT_SUB   = "#6b7fa3"
BORDER     = "#1e2a45"

STATUS_COLOR = {
    "Applied":   "#00d4ff",
    "Interview": "#ffd166",
    "Offer":     "#06d6a0",
    "Rejected":  "#ef476f",
}
PRIORITY_COLOR = {"High": "#ef476f", "Normal": "#00d4ff", "Low": "#6b7fa3"}
STATUSES   = ["Applied", "Interview", "Offer", "Rejected"]
PRIORITIES = ["High", "Normal", "Low"]
SORTS      = ["Date (Newest)", "Company A-Z", "Status", "Priority"]
SORT_KEYS  = {"Date (Newest)": "date_applied", "Company A-Z": "company",
              "Status": "status", "Priority": "priority"}

MOTIVATIONAL_QUOTES = [
    ("\"The secret of getting ahead is getting started.\"", "— Mark Twain"),
    ("\"Believe you can and you're halfway there.\"", "— Theodore Roosevelt"),
    ("\"Every expert was once a beginner.\"", "— Helen Hayes"),
    ("\"Your only limit is your mind.\"", "— Anonymous"),
    ("\"Dream big. Work hard. Stay focused.\"", "— Anonymous"),
    ("\"Success is not final; failure is not fatal.\"", "— Winston Churchill"),
    ("\"The harder you work, the luckier you get.\"", "— Gary Player"),
    ("\"Don't watch the clock; do what it does. Keep going.\"", "— Sam Levenson"),
    ("\"Opportunities don't happen. You create them.\"", "— Chris Grosser"),
    ("\"Push yourself, because no one else is going to do it for you.\"", "— Anonymous"),
    ("\"Great things never come from comfort zones.\"", "— Anonymous"),
    ("\"It always seems impossible until it's done.\"", "— Nelson Mandela"),
    ("\"You are braver than you believe.\"", "— A.A. Milne"),
    ("\"The future belongs to those who believe in their dreams.\"", "— Eleanor Roosevelt"),
    ("\"Act as if what you do makes a difference. It does.\"", "— William James"),
]

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def styled_entry(parent, textvariable=None, show=None, width=28):
    e = tk.Entry(parent, textvariable=textvariable, show=show,
                 bg=BG_INPUT, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=("Consolas", 11),
                 bd=8, width=width)
    e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=ACCENT,
                                             highlightthickness=1,
                                             highlightcolor=ACCENT))
    e.bind("<FocusOut>", lambda _: e.config(highlightthickness=0))
    return e

def styled_btn(parent, text, command, bg=ACCENT, fg=BG, font_size=10, padx=18, pady=9):
    b = tk.Button(parent, text=text, command=command,
                  bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                  font=("Consolas", font_size, "bold"),
                  relief="flat", cursor="hand2", padx=padx, pady=pady,
                  bd=0)
    b.bind("<Enter>", lambda _: b.config(bg=_lighten(bg)))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    return b

def _lighten(hex_color):
    try:
        h = hex_color.lstrip("#")
        r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r,g,b = min(255,r+30), min(255,g+30), min(255,b+30)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color

def setup_ttk_styles():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("T.Treeview", background=BG_CARD, foreground=TEXT,
                fieldbackground=BG_CARD, rowheight=40, borderwidth=0,
                font=("Consolas", 10))
    s.configure("T.Treeview.Heading", background=BG_INPUT, foreground=ACCENT,
                font=("Consolas", 10, "bold"), borderwidth=0, relief="flat")
    s.map("T.Treeview", background=[("selected", ACCENT2)],
          foreground=[("selected", TEXT)])
    s.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT,
                foreground=TEXT, arrowcolor=ACCENT, borderwidth=0)
    s.map("TCombobox", fieldbackground=[("readonly", BG_INPUT)],
          foreground=[("readonly", TEXT)], selectbackground=[("readonly", BG_INPUT)])
    s.configure("Vertical.TScrollbar", background=BG_INPUT,
                troughcolor=BG, borderwidth=0, arrowcolor=TEXT_SUB)

# ══════════════════════════════════════════════════════════════
#  LOGIN / REGISTER WINDOW
# ══════════════════════════════════════════════════════════════
class AuthWindow(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success  = on_success
        self.mode        = "login"   # or "register"
        self.title("JobTrack — Login")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", master.destroy)
        self._build()
        self.grab_set()

    def _build(self):
        # Gradient-like top strip
        top = tk.Frame(self, bg=ACCENT2, height=5)
        top.pack(fill="x")

        # Logo
        tk.Label(self, text="💼", font=("Segoe UI Emoji", 40),
                 bg=BG, fg=ACCENT).pack(pady=(30, 4))
        tk.Label(self, text="JobTrack", font=("Consolas", 26, "bold"),
                 bg=BG, fg=ACCENT).pack()
        tk.Label(self, text="Your personal career command centre",
                 font=("Consolas", 10), bg=BG, fg=TEXT_SUB).pack(pady=(2, 24))

        # Tab buttons
        tab_frame = tk.Frame(self, bg=BG_CARD, pady=2)
        tab_frame.pack(fill="x", padx=50)
        self.login_tab = tk.Button(tab_frame, text="LOGIN",
                                   font=("Consolas", 10, "bold"),
                                   bg=ACCENT, fg=BG, relief="flat",
                                   cursor="hand2", pady=8,
                                   command=lambda: self._switch("login"))
        self.login_tab.pack(side="left", expand=True, fill="x")
        self.reg_tab = tk.Button(tab_frame, text="REGISTER",
                                 font=("Consolas", 10, "bold"),
                                 bg=BG_CARD, fg=TEXT_SUB, relief="flat",
                                 cursor="hand2", pady=8,
                                 command=lambda: self._switch("register"))
        self.reg_tab.pack(side="left", expand=True, fill="x")

        # Form area
        self.form = tk.Frame(self, bg=BG)
        self.form.pack(fill="both", expand=True, padx=50, pady=20)
        self._build_login_form()

    def _switch(self, mode):
        self.mode = mode
        for w in self.form.winfo_children():
            w.destroy()
        if mode == "login":
            self.login_tab.config(bg=ACCENT, fg=BG)
            self.reg_tab.config(bg=BG_CARD, fg=TEXT_SUB)
            self._build_login_form()
        else:
            self.login_tab.config(bg=BG_CARD, fg=TEXT_SUB)
            self.reg_tab.config(bg=ACCENT, fg=BG)
            self._build_register_form()

    def _field(self, parent, label, show=None):
        tk.Label(parent, text=label, bg=BG, fg=TEXT_SUB,
                 font=("Consolas", 9), anchor="w").pack(fill="x", pady=(10, 2))
        var = tk.StringVar()
        e   = styled_entry(parent, textvariable=var, show=show)
        e.pack(fill="x", ipady=4)
        return var

    def _build_login_form(self):
        self.uvar = self._field(self.form, "USERNAME")
        self.pvar = self._field(self.form, "PASSWORD", show="●")

        self.msg_lbl = tk.Label(self.form, text="", bg=BG,
                                font=("Consolas", 9), fg=DANGER)
        self.msg_lbl.pack(pady=(8, 0))

        styled_btn(self.form, "🚀  LOGIN", self._do_login,
                   bg=ACCENT, padx=0).pack(fill="x", pady=(12, 0))

        tk.Label(self.form, text="Don't have an account? Click REGISTER above.",
                 bg=BG, fg=TEXT_SUB, font=("Consolas", 8)).pack(pady=(12, 0))

        # Bind Enter key
        self.bind("<Return>", lambda _: self._do_login())

    def _build_register_form(self):
        self.uvar = self._field(self.form, "CHOOSE A USERNAME")
        self.pvar = self._field(self.form, "CHOOSE A PASSWORD", show="●")
        self.p2var= self._field(self.form, "CONFIRM PASSWORD", show="●")

        self.msg_lbl = tk.Label(self.form, text="", bg=BG,
                                font=("Consolas", 9), fg=DANGER)
        self.msg_lbl.pack(pady=(8, 0))

        styled_btn(self.form, "✅  CREATE ACCOUNT", self._do_register,
                   bg=SUCCESS, fg=BG, padx=0).pack(fill="x", pady=(12, 0))
        self.bind("<Return>", lambda _: self._do_register())

    def _do_login(self):
        u = self.uvar.get().strip()
        p = self.pvar.get().strip()
        if not u or not p:
            self.msg_lbl.config(text="⚠  Please fill in all fields.", fg=WARNING)
            return
        ok, msg = verify_user(u, p)
        if ok:
            self.destroy()
            self.on_success(u)
        else:
            self.msg_lbl.config(text=f"✖  {msg}", fg=DANGER)

    def _do_register(self):
        u  = self.uvar.get().strip()
        p  = self.pvar.get().strip()
        p2 = self.p2var.get().strip()
        if not u or not p:
            self.msg_lbl.config(text="⚠  Please fill in all fields.", fg=WARNING)
            return
        if p != p2:
            self.msg_lbl.config(text="✖  Passwords do not match!", fg=DANGER)
            return
        if len(p) < 4:
            self.msg_lbl.config(text="✖  Password must be at least 4 characters.", fg=DANGER)
            return
        ok, msg = register_user(u, p)
        if ok:
            self.msg_lbl.config(text="✅  " + msg + "  Now login!", fg=SUCCESS)
            self._switch("login")
        else:
            self.msg_lbl.config(text="✖  " + msg, fg=DANGER)

# ══════════════════════════════════════════════════════════════
#  GREETING / MOTIVATION WINDOW
# ══════════════════════════════════════════════════════════════
class GreetingWindow(tk.Toplevel):
    def __init__(self, master, username, on_continue):
        super().__init__(master)
        self.on_continue = on_continue
        self.title("Welcome!")
        self.geometry("560x480")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", master.destroy)
        self._build(username)
        self.grab_set()

    def _build(self, username):
        # Top accent strip
        tk.Frame(self, bg=ACCENT, height=4).pack(fill="x")

        # Stars decoration
        tk.Label(self, text="✦  ✦  ✦",
                 font=("Consolas", 14), bg=BG, fg=ACCENT2).pack(pady=(28, 4))

        # Greeting
        hour = __import__("datetime").datetime.now().hour
        if hour < 12:
            tod = "Good Morning"
            emoji = "🌅"
        elif hour < 17:
            tod = "Good Afternoon"
            emoji = "☀️"
        else:
            tod = "Good Evening"
            emoji = "🌙"

        tk.Label(self, text=f"{emoji}  {tod},",
                 font=("Consolas", 16), bg=BG, fg=TEXT_SUB).pack()
        tk.Label(self, text=username.upper() + "!",
                 font=("Consolas", 30, "bold"), bg=BG, fg=ACCENT).pack(pady=(2, 20))

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=60)

        # Random quote
        quote, author = random.choice(MOTIVATIONAL_QUOTES)

        tk.Label(self, text="TODAY'S MOTIVATION",
                 font=("Consolas", 8, "bold"), bg=BG,
                 fg=ACCENT2).pack(pady=(20, 8))

        q_frame = tk.Frame(self, bg=BG_CARD, padx=28, pady=20,
                           highlightbackground=ACCENT2, highlightthickness=1)
        q_frame.pack(padx=50, fill="x")

        tk.Label(q_frame, text="\u201c",
                 font=("Georgia", 40), bg=BG_CARD, fg=ACCENT2).pack(anchor="w")
        tk.Label(q_frame, text=quote.strip('"'),
                 font=("Georgia", 13, "italic"), bg=BG_CARD, fg=TEXT,
                 wraplength=400, justify="center").pack()
        tk.Label(q_frame, text=author,
                 font=("Consolas", 10), bg=BG_CARD, fg=GOLD).pack(pady=(8, 0))

        # Stats teaser
        summary = tracker.get_summary()
        tk.Label(self, text=f"You have {summary['Total']} application(s) tracked  •  "
                            f"{summary['Interview']} interview(s) pending",
                 font=("Consolas", 9), bg=BG, fg=TEXT_SUB).pack(pady=(20, 4))

        # Continue button
        styled_btn(self, "  Enter Dashboard  →", self._go,
                   bg=ACCENT2, fg=TEXT, font_size=11,
                   padx=30, pady=12).pack(pady=(16, 0))

    def _go(self):
        self.destroy()
        self.on_continue()

# ══════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════
class Dashboard(tk.Frame):
    def __init__(self, master, username):
        super().__init__(master, bg=BG)
        self.pack(fill="both", expand=True)
        self.username = username
        setup_ttk_styles()
        self._build()
        self.refresh_table()

    # ── Layout ──────────────────────────────────────────────────
    def _build(self):
        # ── Top nav ──
        nav = tk.Frame(self, bg=BG_CARD, pady=10,
                       highlightbackground=BORDER, highlightthickness=1)
        nav.pack(fill="x")
        tk.Label(nav, text="💼  JobTrack",
                 font=("Consolas", 18, "bold"), bg=BG_CARD, fg=ACCENT).pack(side="left", padx=20)
        tk.Label(nav, text=f"👤  {self.username}",
                 font=("Consolas", 10), bg=BG_CARD, fg=TEXT_SUB).pack(side="right", padx=20)
        tk.Label(nav, text=f"📅  {date.today().strftime('%d %b %Y')}",
                 font=("Consolas", 10), bg=BG_CARD, fg=TEXT_SUB).pack(side="right", padx=10)

        # ── Summary cards ──
        self.cards_frame = tk.Frame(self, bg=BG, pady=10)
        self.cards_frame.pack(fill="x", padx=20)
        self._build_cards()

        # ── Body ──
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        # Left side
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        self._build_toolbar(left)
        self._build_table(left)

        # Right panel (form + activity)
        right = tk.Frame(body, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1,
                         width=360)
        right.grid(row=0, column=1, sticky="ns")
        right.pack_propagate(False)
        self._build_right_panel(right)

    # ── Summary cards ────────────────────────────────────────────
    def _build_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        summary = tracker.get_summary()
        stats   = tracker.get_streak_and_stats()
        items = [
            ("TOTAL",      summary["Total"],          TEXT_SUB,                   "📋"),
            ("APPLIED",    summary["Applied"],         STATUS_COLOR["Applied"],    "📤"),
            ("INTERVIEW",  summary["Interview"],       STATUS_COLOR["Interview"],  "🗓"),
            ("OFFER",      summary["Offer"],           STATUS_COLOR["Offer"],      "🏆"),
            ("REJECTED",   summary["Rejected"],        STATUS_COLOR["Rejected"],   "❌"),
            ("THIS WEEK",  stats["this_week"],         ACCENT2,                    "📆"),
            ("SUCCESS %",  f"{stats['success_rate']}%", GOLD,                     "⭐"),
        ]
        for label, count, color, icon in items:
            c = tk.Frame(self.cards_frame, bg=BG_CARD,
                         highlightbackground=color, highlightthickness=1,
                         padx=14, pady=10)
            c.pack(side="left", padx=(0, 8))
            tk.Label(c, text=icon, font=("Segoe UI Emoji", 16),
                     bg=BG_CARD, fg=color).pack()
            tk.Label(c, text=str(count), font=("Consolas", 18, "bold"),
                     bg=BG_CARD, fg=color).pack()
            tk.Label(c, text=label, font=("Consolas", 7, "bold"),
                     bg=BG_CARD, fg=TEXT_SUB).pack()

    # ── Toolbar ──────────────────────────────────────────────────
    def _build_toolbar(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        bar.columnconfigure(1, weight=1)

        tk.Label(bar, text="🔍", bg=BG, fg=TEXT_SUB,
                 font=("Consolas", 13)).grid(row=0, column=0, padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        e = styled_entry(bar, textvariable=self.search_var, width=20)
        e.grid(row=0, column=1, sticky="ew", ipady=3)

        # Status filter
        tk.Label(bar, text="Status", bg=BG, fg=TEXT_SUB,
                 font=("Consolas", 9)).grid(row=0, column=2, padx=(10,4))
        self.filter_var = tk.StringVar(value="All")
        cb = ttk.Combobox(bar, textvariable=self.filter_var,
                          values=["All"]+STATUSES, state="readonly", width=11,
                          font=("Consolas", 10))
        cb.grid(row=0, column=3)
        cb.bind("<<ComboboxSelected>>", lambda _: self.refresh_table())

        # Priority filter
        tk.Label(bar, text="Priority", bg=BG, fg=TEXT_SUB,
                 font=("Consolas", 9)).grid(row=0, column=4, padx=(10,4))
        self.priority_filter_var = tk.StringVar(value="All")
        cb2 = ttk.Combobox(bar, textvariable=self.priority_filter_var,
                           values=["All"]+PRIORITIES, state="readonly", width=9,
                           font=("Consolas", 10))
        cb2.grid(row=0, column=5)
        cb2.bind("<<ComboboxSelected>>", lambda _: self.refresh_table())

        # Sort
        tk.Label(bar, text="Sort", bg=BG, fg=TEXT_SUB,
                 font=("Consolas", 9)).grid(row=0, column=6, padx=(10,4))
        self.sort_var = tk.StringVar(value="Date (Newest)")
        cb3 = ttk.Combobox(bar, textvariable=self.sort_var,
                           values=list(SORTS), state="readonly", width=13,
                           font=("Consolas", 10))
        cb3.grid(row=0, column=7, padx=(0, 8))
        cb3.bind("<<ComboboxSelected>>", lambda _: self.refresh_table())

    # ── Table ────────────────────────────────────────────────────
    def _build_table(self, parent):
        cols = ("ID","Company","Role","Date","Status","Priority","Notes")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings",
                                 style="T.Treeview", selectmode="browse")
        widths = {"ID":40,"Company":150,"Role":160,"Date":100,
                  "Status":95,"Priority":80,"Notes":160}
        for col in cols:
            self.tree.heading(col, text=col)
            anchor = "center" if col in ("ID","Date","Status","Priority") else "w"
            self.tree.column(col, width=widths[col], anchor=anchor, minwidth=30)

        sb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        sb.grid(row=1, column=1, sticky="ns")
        parent.rowconfigure(1, weight=1)

        # Action row
        act = tk.Frame(parent, bg=BG)
        act.grid(row=2, column=0, sticky="ew", pady=(8,0))
        styled_btn(act, "✏️  Edit", self._load_edit, bg=ACCENT, fg=BG, pady=7).pack(side="left", padx=(0,6))
        styled_btn(act, "🗑️  Delete", self._delete, bg=DANGER, pady=7).pack(side="left", padx=(0,6))
        styled_btn(act, "📋  Duplicate", self._duplicate, bg=BG_HOVER, fg=TEXT, pady=7).pack(side="left")
        styled_btn(act, "🔄", self.refresh_table, bg=BG_CARD, fg=TEXT_SUB, pady=7, padx=10).pack(side="right")

    # ── Right panel ──────────────────────────────────────────────
    def _build_right_panel(self, parent):
        # Tabs
        tab_bar = tk.Frame(parent, bg=BG_CARD)
        tab_bar.pack(fill="x")
        self.panel_mode = tk.StringVar(value="form")
        for label, val in [("✏️ Form", "form"), ("📜 Activity", "activity")]:
            b = tk.Button(tab_bar, text=label, bg=BG_INPUT, fg=TEXT_SUB,
                          font=("Consolas", 9, "bold"), relief="flat",
                          cursor="hand2", pady=7,
                          command=lambda v=val: self._switch_panel(v))
            b.pack(side="left", expand=True, fill="x")

        self.panel_container = tk.Frame(parent, bg=BG_CARD)
        self.panel_container.pack(fill="both", expand=True)
        self._show_form_panel()

    def _switch_panel(self, mode):
        self.panel_mode.set(mode)
        for w in self.panel_container.winfo_children():
            w.destroy()
        if mode == "form":
            self._show_form_panel()
        else:
            self._show_activity_panel()

    def _show_form_panel(self):
        p = self.panel_container
        self.edit_id = None

        # Make form scrollable so nothing gets cut off
        canvas = tk.Canvas(p, bg=BG_CARD, highlightthickness=0)
        sb = ttk.Scrollbar(p, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_CARD)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        inner.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel scroll
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(inner, text="ADD APPLICATION", font=("Consolas", 11, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(pady=(14,10), padx=16)

        def field(lbl, show=None):
            tk.Label(inner, text=lbl, bg=BG_CARD, fg=TEXT_SUB,
                     font=("Consolas", 8), anchor="w").pack(fill="x", padx=16, pady=(6,1))
            var = tk.StringVar()
            e = styled_entry(inner, textvariable=var, show=show, width=26)
            e.pack(fill="x", padx=16, ipady=3)
            return var

        self.company_var  = field("COMPANY *")
        self.role_var     = field("ROLE / POSITION *")
        self.date_var     = field("DATE APPLIED")
        self.date_var.set(str(date.today()))
        self.salary_var   = field("SALARY / PACKAGE (optional)")
        self.location_var = field("LOCATION (optional)")
        self.notes_var    = field("NOTES")

        for lbl, attr, vals in [
            ("STATUS", "status_var", STATUSES),
            ("PRIORITY", "priority_var", PRIORITIES),
        ]:
            tk.Label(inner, text=lbl, bg=BG_CARD, fg=TEXT_SUB,
                     font=("Consolas", 8), anchor="w").pack(fill="x", padx=16, pady=(6,1))
            var = tk.StringVar(value=vals[0] if lbl=="STATUS" else "Normal")
            setattr(self, attr, var)
            cb = ttk.Combobox(inner, textvariable=var, values=vals,
                              state="readonly", font=("Consolas", 10))
            cb.pack(fill="x", padx=16)

        self.msg_lbl = tk.Label(inner, text="", bg=BG_CARD,
                                font=("Consolas", 8), fg=DANGER)
        self.msg_lbl.pack(pady=(6,0))

        self.submit_btn = styled_btn(inner, "➕  ADD APPLICATION",
                                     self._submit, bg=SUCCESS, fg=BG, padx=0)
        self.submit_btn.pack(fill="x", padx=16, pady=(8,4))
        styled_btn(inner, "✖  CLEAR", self._clear_form,
                   bg=BG_INPUT, fg=TEXT_SUB, padx=0).pack(fill="x", padx=16, pady=(0,16))

    def _show_activity_panel(self):
        p = self.panel_container
        tk.Label(p, text="RECENT ACTIVITY", font=("Consolas", 11, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(pady=(14,10), padx=16)

        canvas = tk.Canvas(p, bg=BG_CARD, highlightthickness=0)
        sb = ttk.Scrollbar(p, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_CARD)
        canvas.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        activity = load_activity()
        if not activity:
            tk.Label(inner, text="No activity yet.\nStart adding applications!",
                     bg=BG_CARD, fg=TEXT_SUB, font=("Consolas", 9),
                     justify="center").pack(pady=30)
        for item in activity:
            row = tk.Frame(inner, bg=BG_INPUT, pady=8, padx=10)
            row.pack(fill="x", padx=12, pady=3)
            action_colors = {"Added": SUCCESS, "Updated": WARNING, "Deleted": DANGER}
            color = action_colors.get(item["action"], TEXT_SUB)
            tk.Label(row, text=f"● {item['action']}",
                     font=("Consolas", 9, "bold"), bg=BG_INPUT, fg=color).pack(anchor="w")
            tk.Label(row, text=item["detail"],
                     font=("Consolas", 9), bg=BG_INPUT, fg=TEXT).pack(anchor="w")
            tk.Label(row, text=item["time"],
                     font=("Consolas", 8), bg=BG_INPUT, fg=TEXT_SUB).pack(anchor="w")

    # ── Table refresh ────────────────────────────────────────────
    def refresh_table(self, *_):
        kw      = self.search_var.get() if hasattr(self, "search_var") else ""
        status  = self.filter_var.get() if hasattr(self, "filter_var") else "All"
        prio    = self.priority_filter_var.get() if hasattr(self, "priority_filter_var") else "All"
        sort_lbl= self.sort_var.get() if hasattr(self, "sort_var") else "Date (Newest)"
        sort_key= SORT_KEYS.get(sort_lbl, "date_applied")

        apps = tracker.search_applications(kw, status, prio, sort_key)
        for row in self.tree.get_children():
            self.tree.delete(row)

        for app in apps:
            s = app.get("status","Applied")
            pr= app.get("priority","Normal")
            sc= STATUS_COLOR.get(s, TEXT)
            pc= PRIORITY_COLOR.get(pr, TEXT_SUB)
            tag_s = f"s_{s}"
            tag_p = f"p_{pr}"
            self.tree.tag_configure(tag_s, foreground=sc)
            self.tree.insert("", "end", iid=app["id"], tags=(tag_s,),
                             values=(app["id"], app["company"], app["role"],
                                     app["date_applied"], s, pr,
                                     app.get("notes","")))
        self._build_cards()

    # ── Actions ──────────────────────────────────────────────────
    def _load_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a row to edit.")
            return
        app_id = int(sel[0])
        apps   = tracker.get_all_applications()
        app    = next((a for a in apps if a["id"] == app_id), None)
        if not app:
            return
        self._switch_panel("form")
        self.edit_id = app_id
        self.company_var.set(app["company"])
        self.role_var.set(app["role"])
        self.date_var.set(app["date_applied"])
        self.salary_var.set(app.get("salary",""))
        self.location_var.set(app.get("location",""))
        self.notes_var.set(app.get("notes",""))
        self.status_var.set(app["status"])
        self.priority_var.set(app.get("priority","Normal"))
        self.submit_btn.config(text="💾  SAVE CHANGES", bg=WARNING, fg=BG)

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return
        if messagebox.askyesno("Delete", f"Delete application #{sel[0]}?"):
            tracker.delete_application(int(sel[0]))
            self.refresh_table()
            self._clear_form()

    def _duplicate(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a row to duplicate.")
            return
        apps = tracker.get_all_applications()
        app  = next((a for a in apps if a["id"] == int(sel[0])), None)
        if app:
            tracker.add_application(app["company"], app["role"],
                                    str(date.today()), "Applied",
                                    app.get("notes",""),
                                    app.get("priority","Normal"))
            self.refresh_table()

    def _submit(self):
        company  = self.company_var.get().strip()
        role     = self.role_var.get().strip()
        d        = self.date_var.get().strip()
        status   = self.status_var.get()
        priority = self.priority_var.get()
        notes    = self.notes_var.get().strip()
        salary   = self.salary_var.get().strip()
        location = self.location_var.get().strip()

        if not company or not role:
            self.msg_lbl.config(text="⚠  Company and Role are required.", fg=DANGER)
            return
        self.msg_lbl.config(text="")

        if self.edit_id is None:
            app = tracker.add_application(company, role, d, status, notes, priority)
            tracker.update_application(app["id"], salary=salary, location=location)
        else:
            tracker.update_application(self.edit_id, company=company, role=role,
                                       date_applied=d, status=status, notes=notes,
                                       priority=priority, salary=salary, location=location)
        self.refresh_table()
        self._clear_form()
        if self.panel_mode.get() == "activity":
            self._show_activity_panel()

    def _clear_form(self):
        if not hasattr(self, "company_var"):
            return
        self.edit_id = None
        self.company_var.set("")
        self.role_var.set("")
        self.date_var.set(str(date.today()))
        self.salary_var.set("")
        self.location_var.set("")
        self.notes_var.set("")
        self.status_var.set("Applied")
        self.priority_var.set("Normal")
        self.msg_lbl.config(text="")
        self.submit_btn.config(text="➕  ADD APPLICATION", bg=SUCCESS, fg=BG)

# ══════════════════════════════════════════════════════════════
#  APP ROOT
# ══════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JobTrack")
        self.geometry("1280x800")
        self.minsize(960, 620)
        self.configure(bg=BG)
        self.withdraw()   # hide until login done
        self._start_auth()

    def _start_auth(self):
        AuthWindow(self, self._on_login)

    def _on_login(self, username):
        set_current_user(username)  # ← switch to this user's data files
        log_activity("Login", f"{username} signed in")
        GreetingWindow(self, username, lambda: self._show_dashboard(username))

    def _show_dashboard(self, username):
        self.deiconify()
        Dashboard(self, username)

if __name__ == "__main__":
    App().mainloop()
