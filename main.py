# ══════════════════════════════════════════════════════════════════
#  ONE TAG ONE NATION  —  Toll Management System
#  DUAL PORTAL: User Portal  +  Admin Portal
#  Fixed: ADMIN_LOG trigger compatibility, password hashing,
#         proper role-based login, missing sequences added
#  Updated: User Recharge option added to User Portal
# ══════════════════════════════════════════════════════════════════

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime
import math
import sys
import hashlib

# ══════════════════════════════════════════════════════════════════
#  ORACLE DB CONFIG  ← edit password / dsn if needed
# ══════════════════════════════════════════════════════════════════
DB_CONFIG = {
    "user":     "system",
    "password": "M@r19y@M",
    "dsn":      "localhost:1521/orcl1",
}

# ══════════════════════════════════════════════════════════════════
#  DB CONNECTION
# ══════════════════════════════════════════════════════════════════
try:
    import oracledb
    _conn  = oracledb.connect(**DB_CONFIG)
    _cur   = _conn.cursor()
    DB_OK  = True
    DB_ERR = ""
except Exception as _e:
    DB_OK  = False
    DB_ERR = str(_e)
    _conn  = None
    _cur   = None


def db_exec(sql, params=(), commit=False):
    if not DB_OK:
        return False
    try:
        _cur.execute(sql, params)
        if commit:
            _conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return False


def db_fetch(sql, params=()):
    if not DB_OK:
        return []
    try:
        _cur.execute(sql, params)
        return _cur.fetchall()
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return []


def db_fetchone(sql, params=()):
    if not DB_OK:
        return None
    try:
        _cur.execute(sql, params)
        return _cur.fetchone()
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return None


# ══════════════════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

C_BG     = "#F0F4F8"
C_PANEL  = "#FFFFFF"
C_BORDER = "#CBD5E1"
C_ACCENT = "#1D5FA8"
C_ACT2   = "#D95F02"
C_GREEN  = "#2E7D32"
C_RED    = "#C62828"
C_YELLOW = "#E65100"
C_TEXT   = "#1A202C"
C_MUTED  = "#64748B"
C_HEADER = "#1D5FA8"
C_SIDE   = "#EEF2F7"
C_SHOV   = "#DBEAFE"
C_THBG   = "#E2E8F0"
C_TROW   = "#FFFFFF"
C_TALT   = "#F8FAFC"

# Admin portal uses a distinct darker theme
C_ADMIN_HEADER = "#1A1A2E"
C_ADMIN_SIDE   = "#16213E"
C_ADMIN_SHOV   = "#0F3460"
C_ADMIN_ACCENT = "#E94560"

FL = ("Segoe UI", 10)
FH = ("Segoe UI", 12, "bold")
FS = ("Segoe UI", 9)
FM = ("Consolas", 10)


# ══════════════════════════════════════════════════════════════════
#  WIDGET FACTORIES
# ══════════════════════════════════════════════════════════════════
def frm(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=C_PANEL, corner_radius=10,
                        border_width=1, border_color=C_BORDER, **kw)

def lbl(parent, text, font=FL, color=C_TEXT, **kw):
    return ctk.CTkLabel(parent, text=text, font=font,
                        text_color=color, **kw)

def ent(parent, ph="", width=210, show=""):
    return ctk.CTkEntry(parent, placeholder_text=ph, font=FM,
                        width=width, fg_color="#F8FAFC",
                        border_color=C_BORDER, text_color=C_TEXT,
                        corner_radius=6, show=show)

def btn(parent, text, cmd, color=C_ACCENT, width=150, icon=""):
    t = f"{icon}  {text}" if icon else text
    return ctk.CTkButton(parent, text=t, command=cmd,
                         fg_color=color, hover_color=color + "CC",
                         font=(FL[0], FL[1], "bold"),
                         width=width, corner_radius=8,
                         text_color="#FFFFFF")

def cmb(parent, values, width=210):
    v = values if values else ["—"]
    return ctk.CTkComboBox(parent, values=v, width=width,
                           fg_color="#F8FAFC", border_color=C_BORDER,
                           button_color=C_ACCENT, text_color=C_TEXT,
                           font=FM, corner_radius=6,
                           dropdown_fg_color=C_PANEL,
                           dropdown_text_color=C_TEXT)

def mktable(parent, cols, height=10):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("T.Treeview",
        background=C_TROW, fieldbackground=C_TROW,
        foreground=C_TEXT, font=FS, rowheight=28,
        borderwidth=0, relief="flat")
    style.configure("T.Treeview.Heading",
        background=C_THBG, foreground=C_ACCENT,
        font=(FH[0], FH[1] - 1, "bold"),
        relief="flat", padding=6)
    style.map("T.Treeview",
        background=[("selected", "#BFDBFE")],
        foreground=[("selected", C_TEXT)])

    wrap = ctk.CTkFrame(parent, fg_color=C_PANEL, corner_radius=8,
                        border_width=1, border_color=C_BORDER)
    tree = ttk.Treeview(wrap, columns=cols, show="headings",
                        style="T.Treeview", height=height,
                        selectmode="browse")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=max(80, len(c) * 9),
                    anchor="center", minwidth=60)
    tree.tag_configure("alt", background=C_TALT)

    vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    wrap.grid_rowconfigure(0, weight=1)
    wrap.grid_columnconfigure(0, weight=1)
    return wrap, tree

def fill(tree, rows):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tree.insert("", "end", values=row,
                    tags=("alt",) if i % 2 else ())

def sec(parent, text, row, col=0, span=4):
    f = ctk.CTkFrame(parent, fg_color="#EFF6FF", corner_radius=6,
                     border_width=1, border_color="#BFDBFE", height=32)
    f.grid(row=row, column=col, columnspan=span,
           sticky="ew", padx=10, pady=(12, 4))
    ctk.CTkLabel(f, text=f"  ▸  {text}",
                 font=(FH[0], FH[1] - 1, "bold"),
                 text_color=C_ACCENT, anchor="w"
                 ).pack(side="left", padx=8)

def gv(w):
    if isinstance(w, ctk.CTkEntry):    return w.get().strip()
    if isinstance(w, ctk.CTkComboBox): return w.get().strip()
    return ""

def clr(wdict):
    for w in wdict.values():
        if isinstance(w, ctk.CTkEntry):
            w.delete(0, "end")
        elif isinstance(w, ctk.CTkComboBox):
            v = w.cget("values")
            if v: w.set(v[0])

def bform(parent, fields, row=0, cols=2):
    out = {}
    for i, f in enumerate(fields):
        label = f[0]; ph = f[1]
        wfn   = f[2] if len(f) > 2 else None
        c  = (i % cols) * 2
        ro = row + (i // cols)
        ctk.CTkLabel(parent, text=label + ":", font=FL,
                     text_color=C_MUTED, anchor="e"
                     ).grid(row=ro, column=c,
                            sticky="e", padx=(10, 4), pady=5)
        w = wfn(parent) if wfn else ent(parent, ph)
        w.grid(row=ro, column=c + 1,
               sticky="w", padx=(0, 14), pady=5)
        out[label] = w
    return out, row + math.ceil(len(fields) / cols)

def notify(title, msg, kind="info"):
    if kind == "error":     messagebox.showerror(title, msg)
    elif kind == "warning": messagebox.showwarning(title, msg)
    else:                   messagebox.showinfo(title, msg)

def db_banner(parent, row):
    ok_color  = "#F0FDF4" if DB_OK else "#FEF2F2"
    ok_border = "#BBF7D0" if DB_OK else "#FECACA"
    icon  = "● Connected" if DB_OK else "● Offline"
    color = C_GREEN if DB_OK else C_RED
    msg   = f"{icon}  —  {DB_CONFIG['dsn']}" if DB_OK else f"{icon}  —  {DB_ERR[:70]}"
    f = ctk.CTkFrame(parent, fg_color=ok_color, corner_radius=8,
                     border_width=1, border_color=ok_border)
    f.grid(row=row, column=0, columnspan=4,
           padx=10, pady=(4, 8), sticky="ew")
    ctk.CTkLabel(f, text=f"  {msg}", font=FS,
                 text_color=color, anchor="w"
                 ).pack(side="left", padx=10, pady=6)

# ══════════════════════════════════════════════════════════════════
#  DB HELPERS  (fresh cursor every call — fixes shared cursor bug)
# ══════════════════════════════════════════════════════════════════
def db_exec(sql, params=(), commit=False):
    if not DB_OK:
        return False
    try:
        cur = _conn.cursor()
        cur.execute(sql, params)
        if commit:
            _conn.commit()
        cur.close()
        return True
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return False


def db_fetch(sql, params=()):
    if not DB_OK:
        return []
    try:
        cur = _conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchall()
        cur.close()
        return result
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return []


def db_fetchone(sql, params=()):
    if not DB_OK:
        return None
    try:
        cur = _conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()
        cur.close()
        return result
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return None


# ══════════════════════════════════════════════════════════════════
#  LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════
class LoginScreen(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("ONE TAG ONE NATION  —  Login")
        self.geometry("560x700")
        self.resizable(False, False)
        self.configure(fg_color=C_BG)
        self._build()

    def _build(self):
        # ── Header ──────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=C_HEADER, corner_radius=0, height=72)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="◈  ONE TAG ONE NATION",
                     font=("Segoe UI", 20, "bold"),
                     text_color="#FFFFFF").pack(pady=20)

        body = ctk.CTkScrollableFrame(self, fg_color=C_BG, corner_radius=0)
        body.pack(fill="both", expand=True, padx=40, pady=10)

        ctk.CTkLabel(body, text="Toll Management System — Pakistan",
                     font=FS, text_color=C_MUTED).pack(pady=(4, 10))

        # ── Tab switcher ────────────────────────────────────────
        tab_row = ctk.CTkFrame(body, fg_color="#E2E8F0", corner_radius=10)
        tab_row.pack(fill="x", pady=(0, 16))
        self._tab_var = ctk.StringVar(value="login")
        ctk.CTkRadioButton(tab_row, text="🔑  Login",
                           variable=self._tab_var, value="login",
                           font=FH, text_color=C_TEXT, fg_color=C_ACCENT,
                           command=self._show_tab).pack(side="left", padx=20, pady=12)
        ctk.CTkRadioButton(tab_row, text="📝  Sign Up",
                           variable=self._tab_var, value="signup",
                           font=FH, text_color=C_TEXT, fg_color=C_GREEN,
                           command=self._show_tab).pack(side="right", padx=20, pady=12)

        # ── Portal selector ──────────────────────────────────────
        self._portal_frame = ctk.CTkFrame(body, fg_color="#EFF6FF", corner_radius=10,
                                          border_width=1, border_color="#BFDBFE")
        self._portal_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(self._portal_frame, text="Select Portal:",
                     font=FL, text_color=C_MUTED).pack(side="left", padx=14, pady=10)
        self._portal = ctk.StringVar(value="user")
        ctk.CTkRadioButton(self._portal_frame, text="👤 User",
                           variable=self._portal, value="user",
                           font=FL, text_color=C_TEXT, fg_color=C_ACCENT
                           ).pack(side="left", padx=12, pady=10)
        ctk.CTkRadioButton(self._portal_frame, text="🛡 Admin",
                           variable=self._portal, value="admin",
                           font=FL, text_color=C_TEXT, fg_color=C_ADMIN_ACCENT
                           ).pack(side="left", padx=12, pady=10)

        # ── Login form ───────────────────────────────────────────
        self._login_panel = ctk.CTkFrame(body, fg_color=C_PANEL, corner_radius=12,
                                         border_width=1, border_color=C_BORDER)
        self._login_panel.pack(fill="x", pady=4)

        ctk.CTkLabel(self._login_panel, text="Username", font=FL,
                     text_color=C_MUTED, anchor="w").pack(fill="x", padx=20, pady=(18, 2))
        self._uname = ctk.CTkEntry(self._login_panel,
                                   placeholder_text="Enter username",
                                   font=FM, fg_color="#F8FAFC",
                                   border_color=C_BORDER, text_color=C_TEXT,
                                   corner_radius=8, height=40)
        self._uname.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self._login_panel, text="Password", font=FL,
                     text_color=C_MUTED, anchor="w").pack(fill="x", padx=20, pady=(0, 2))
        self._pwd = ctk.CTkEntry(self._login_panel,
                                 placeholder_text="Enter password",
                                 font=FM, fg_color="#F8FAFC",
                                 border_color=C_BORDER, text_color=C_TEXT,
                                 corner_radius=8, height=40, show="●")
        self._pwd.pack(fill="x", padx=20, pady=(0, 14))
        self._pwd.bind("<Return>", lambda e: self._login())

        ctk.CTkButton(self._login_panel, text="Login  →",
                      command=self._login,
                      fg_color=C_ACCENT, hover_color="#1545A0",
                      font=("Segoe UI", 12, "bold"),
                      height=44, corner_radius=8,
                      text_color="#FFFFFF").pack(fill="x", padx=20, pady=(0, 18))

        # ── Sign-up form ─────────────────────────────────────────
        self._signup_panel = ctk.CTkFrame(body, fg_color=C_PANEL, corner_radius=12,
                                          border_width=1, border_color=C_BORDER)

        def _su_field(label, ph, show=""):
            ctk.CTkLabel(self._signup_panel, text=label, font=FL,
                         text_color=C_MUTED, anchor="w").pack(fill="x", padx=20, pady=(10, 2))
            e = ctk.CTkEntry(self._signup_panel, placeholder_text=ph,
                             font=FM, fg_color="#F8FAFC",
                             border_color=C_BORDER, text_color=C_TEXT,
                             corner_radius=8, height=38, show=show)
            e.pack(fill="x", padx=20, pady=(0, 2))
            return e

        ctk.CTkLabel(self._signup_panel,
                     text="  Create Your Account",
                     font=(FH[0], FH[1], "bold"),
                     text_color=C_GREEN, anchor="w"
                     ).pack(fill="x", padx=20, pady=(16, 6))

        self._su_name  = _su_field("Full Name *",        "e.g. Maryam Khan")
        self._su_cnic  = _su_field("CNIC *",             "XXXXX-XXXXXXX-X")
        self._su_phone = _su_field("Phone",              "03XX-XXXXXXX")
        self._su_email = _su_field("Email",              "user@email.com")
        self._su_prov  = _su_field("Province",           "e.g. Punjab")
        self._su_addr  = _su_field("Address",            "Street, City")
        self._su_uname = _su_field("Username *",         "Choose a username")
        self._su_pass  = _su_field("Password *",         "Min 4 characters", show="●")
        self._su_conf  = _su_field("Confirm Password *", "Repeat password",  show="●")

        ctk.CTkButton(self._signup_panel, text="Create Account  ✓",
                      command=self._signup,
                      fg_color=C_GREEN, hover_color="#1B5E20",
                      font=("Segoe UI", 12, "bold"),
                      height=44, corner_radius=8,
                      text_color="#FFFFFF").pack(fill="x", padx=20, pady=(14, 18))

        # ── DB status pill ───────────────────────────────────────
        pill = "#DCFCE7" if DB_OK else "#FEE2E2"
        ptc  = "#166534" if DB_OK else "#991B1B"
        pt   = f"{'● DB Connected' if DB_OK else '● DB Offline'}  |  {DB_CONFIG['dsn']}"
        ctk.CTkLabel(body, text=pt, font=FS,
                     text_color=ptc, fg_color=pill,
                     corner_radius=20).pack(pady=8)

        ctk.CTkLabel(body,
                     text="Demo — User: maryam / 123   Admin: admin / admin123",
                     font=("Segoe UI", 8), text_color=C_MUTED).pack(pady=2)

    # ── Tab switch ───────────────────────────────────────────────
    def _show_tab(self):
        if self._tab_var.get() == "login":
            self._signup_panel.pack_forget()
            self._portal_frame.pack(fill="x", pady=(0, 12))
            self._login_panel.pack(fill="x", pady=4)
        else:
            self._login_panel.pack_forget()
            self._portal_frame.pack_forget()
            self._signup_panel.pack(fill="x", pady=4)

    # ── Sign-up logic ────────────────────────────────────────────
    def _signup(self):
        name  = self._su_name.get().strip()
        cnic  = self._su_cnic.get().strip()
        phone = self._su_phone.get().strip()
        email = self._su_email.get().strip()
        prov  = self._su_prov.get().strip()
        addr  = self._su_addr.get().strip()
        uname = self._su_uname.get().strip()
        pwd   = self._su_pass.get().strip()
        conf  = self._su_conf.get().strip()

        if not name:
            return notify("Validation", "Full Name is required.", "error")
        if not cnic:
            return notify("Validation", "CNIC is required.", "error")
        if not uname:
            return notify("Validation", "Username is required.", "error")
        if not pwd:
            return notify("Validation", "Password is required.", "error")
        if len(pwd) < 4:
            return notify("Validation", "Password must be at least 4 characters.", "error")
        if pwd != conf:
            return notify("Validation", "Passwords do not match.", "error")

        if not DB_OK:
            return notify("Offline", "Sign-up requires a live database connection.", "warning")

        if db_fetchone("SELECT USER_ID FROM USERS WHERE LOWER(USERNAME)=LOWER(:1)", (uname,)):
            return notify("Sign Up Failed",
                          f"Username '{uname}' is already taken.", "error")
        if db_fetchone("SELECT USER_ID FROM USERS WHERE CNIC=:1", (cnic,)):
            return notify("Sign Up Failed",
                          "An account with this CNIC already exists.", "error")

        ok = db_exec(
            "INSERT INTO USERS(USER_ID,NAME,CNIC,PHONE,EMAIL,PROVINCE,ADDRESS,"
            "IS_ACTIVE,USERNAME,PASSWORD) "
            "VALUES(USER_SEQ.NEXTVAL,:1,:2,:3,:4,:5,:6,'Y',:7,:8)",
            (name, cnic, phone or None, email or None,
             prov or None, addr or None, uname, pwd),
            commit=True)
        if not ok:
            return

        role_row = db_fetchone(
            "SELECT ROLE_ID FROM ROLE WHERE UPPER(ROLE_NAME)='CUSTOMER'")
        if role_row:
            db_exec(
                "INSERT INTO USER_ROLE(USER_ROLE_ID,USER_ID,ROLE_ID,ASSIGNED_DATE) "
                "VALUES(USER_ROLE_SEQ.NEXTVAL,"
                "(SELECT USER_ID FROM USERS WHERE LOWER(USERNAME)=LOWER(:1)),:2,SYSDATE)",
                (uname, role_row[0]), commit=True)

        notify("Account Created",
               f"Welcome, {name}!\nAccount created successfully.\n"
               "Please log in with your new credentials.", "info")

        for w in (self._su_name, self._su_cnic, self._su_phone, self._su_email,
                  self._su_prov, self._su_addr, self._su_uname,
                  self._su_pass, self._su_conf):
            w.delete(0, "end")
        self._uname.delete(0, "end")
        self._uname.insert(0, uname)
        self._tab_var.set("login")
        self._show_tab()

    # ── Login logic ──────────────────────────────────────────────
    def _login(self):
        uname  = self._uname.get().strip()
        pwd    = self._pwd.get().strip()
        portal = self._portal.get()

        if not uname or not pwd:
            return notify("Validation", "Please enter username and password.", "error")

        # ── Offline demo mode ────────────────────────────────────
 
        # ── Live DB login ────────────────────────────────────────
        row = db_fetchone(
            "SELECT U.USER_ID, U.NAME, R.ROLE_NAME "
            "FROM USERS U "
            "JOIN USER_ROLE UR ON U.USER_ID = UR.USER_ID "
            "JOIN ROLE R ON UR.ROLE_ID = R.ROLE_ID "
            "WHERE LOWER(U.USERNAME) = LOWER(:1) "
            "AND U.PASSWORD = :2 "
            "AND U.IS_ACTIVE = 'Y' "
            "ORDER BY R.ROLE_ID ASC "
            "FETCH FIRST 1 ROWS ONLY",
            (uname, pwd)
        )

        if not row:
            return notify("Login Failed",
                          "Invalid username or password, or account is inactive.",
                          "error")

        uid, name, role = row
        role = role.upper().strip()

        # ── Role vs portal check ─────────────────────────────────
        admin_roles = {"ADMIN", "PLAZA_MANAGER"}
        user_roles  = {"CUSTOMER"}

        if portal == "admin" and role not in admin_roles:
            return notify("Access Denied",
                          f"Your role ({role}) does not have Admin access.\n"
                          "Please select the User portal.", "error")

        if portal == "user" and role not in user_roles:
            return notify("Access Denied",
                          f"Your role ({role}) requires the Admin portal.", "error")

        # ── Open portal ──────────────────────────────────────────
        if portal == "admin":
            self._open_admin(uid, name, role)
        else:
            self._open_user(uid, name, role)

    def _open_admin(self, uid, name, role):
        self.destroy()
        AdminPortal(uid, name, role).mainloop()

    def _open_user(self, uid, name, role):
        self.destroy()
        UserPortal(uid, name, role).mainloop()

# ══════════════════════════════════════════════════════════════════
#  USER PORTAL
# ══════════════════════════════════════════════════════════════════
class UserPortal(ctk.CTk):
    """Portal for registered customers/drivers."""

    def __init__(self, user_id, name, role):
        super().__init__()
        self.user_id = user_id
        self.user_name = name
        self.user_role = role
        self.title(f"ONE TAG ONE NATION  —  User Portal  |  {name}")
        self.geometry("1280x800")
        self.minsize(1000, 640)
        self.configure(fg_color=C_BG)
        self._build()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._topbar()
        self._sidebar()
        self._content_area()
        self._dash()

    def _topbar(self):
        bar = ctk.CTkFrame(self, fg_color=C_HEADER,
                           corner_radius=0, height=54)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        ctk.CTkLabel(bar, text="  👤  ONE TAG ONE NATION  —  User Portal",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF"
                     ).grid(row=0, column=0, padx=16, sticky="w")

        ctk.CTkLabel(bar,
                     text=f"  Welcome, {self.user_name}  |  ID: {self.user_id}",
                     font=FS, text_color="#BFDBFE"
                     ).grid(row=0, column=1, padx=10)

        logout_btn = ctk.CTkButton(bar, text="Logout  ⇢",
                                   command=self._logout,
                                   fg_color="#C62828", hover_color="#991B1B",
                                   font=FS, width=100, corner_radius=8)
        logout_btn.grid(row=0, column=2, padx=10)

        self._time_lbl = ctk.CTkLabel(bar, text="", font=FS,
                                      text_color="#CBD5E1")
        self._time_lbl.grid(row=0, column=3, padx=20)
        self._tick()

    def _tick(self):
        self._time_lbl.configure(
            text=datetime.now().strftime("  %a %d %b %Y   %H:%M:%S  "))
        self.after(1000, self._tick)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            app = LoginScreen()
            app.mainloop()

    def _sidebar(self):
        sb = ctk.CTkScrollableFrame(self, fg_color=C_SIDE,
                          corner_radius=0, width=200,
                          scrollbar_button_color=C_BORDER,
                          scrollbar_button_hover_color=C_ACCENT)
        sb.grid(row=1, column=0, sticky="nsew")

        MENU = [
            ("Dashboard",           "📊", self._dash),
            ("── MY ACCOUNT",       "",   None),
            ("  My Profile",        "👤", lambda: self._tab("profile")),
            ("  My Vehicles",       "🚗", lambda: self._tab("my_vehicles")),
            ("  My Tags",           "📡", lambda: self._tab("my_tags")),
            ("── RECHARGE",         "",   None),
            ("  Recharge My Tag",   "💳", lambda: self._tab("request_recharge")),
            ("── MY HISTORY",       "",   None),
            ("  Transactions",      "💸", lambda: self._tab("my_txns")),
            ("  Recharge History",  "🧾", lambda: self._tab("my_recharges")),
            ("  Payment History",   "💵", lambda: self._tab("my_payments")),
            ("── MY STATUS",        "",   None),
            ("  My Alerts",         "🔔", lambda: self._tab("my_alerts")),
            ("  My Exemptions",     "🏷", lambda: self._tab("my_exemptions")),
            ("── FEEDBACK",         "",   None),
            ("  Feedback",          "💬", lambda: self._tab("feedback")),
        ]

        for text, icon, cmd in MENU:
            if text.startswith("──"):
                ctk.CTkLabel(sb, text=f"  {text}",
                             font=("Segoe UI", 8, "bold"),
                             text_color=C_MUTED, anchor="w"
                             ).pack(fill="x", padx=6, pady=(10, 2))
            elif cmd is None:
                pass
            else:
                t = f" {icon}  {text.strip()}" if icon else f"  {text.strip()}"
                ctk.CTkButton(sb, text=t,
                              command=lambda c=cmd: c(),
                              fg_color="transparent",
                              hover_color=C_SHOV,
                              text_color=C_TEXT, anchor="w",
                              font=FL, height=34, corner_radius=8
                              ).pack(fill="x", padx=8, pady=1)

    def _content_area(self):
        self.pane = ctk.CTkScrollableFrame(
            self, fg_color=C_BG, corner_radius=0,
            scrollbar_button_color=C_BORDER,
            scrollbar_button_hover_color=C_ACCENT)
        self.pane.grid(row=1, column=1, sticky="nsew")
        self.pane.grid_columnconfigure(0, weight=1)

    def _reset(self):
        for w in self.pane.winfo_children():
            w.destroy()

    def _title(self, title, sub=""):
        p = self.pane
        ctk.CTkLabel(p, text=title,
                     font=("Segoe UI", 20, "bold"),
                     text_color=C_ACCENT, anchor="w"
                     ).grid(row=0, column=0, columnspan=4,
                            sticky="w", padx=20, pady=(20, 2))
        if sub:
            ctk.CTkLabel(p, text=sub, font=FS,
                         text_color=C_MUTED, anchor="w"
                         ).grid(row=1, column=0, columnspan=4,
                                sticky="w", padx=22, pady=(0, 4))
        db_banner(p, 2)
        return 3

    def _tab(self, key):
        self._reset()
        {
            "profile":          self._profile,
            "my_vehicles":      self._my_vehicles,
            "my_tags":          self._my_tags,
            "request_recharge": self._request_recharge,
            "my_txns":          self._my_txns,
            "my_recharges":     self._my_recharges,
            "my_payments":      self._my_payments,
            "my_alerts":        self._my_alerts,
            "my_exemptions":    self._my_exemptions,
            "feedback":         self._feedback,
        }[key]()

    # ── USER DASHBOARD ──────────────────────────────────────────
    def _dash(self):
        self._reset()
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(p, text=f"👋  Welcome back, {self.user_name}!",
                     font=("Segoe UI", 20, "bold"),
                     text_color=C_ACCENT, anchor="w"
                     ).grid(row=0, column=0, columnspan=4,
                            sticky="w", padx=20, pady=(20, 4))
        db_banner(p, 1)

        def q(sql, params=()):
            r = db_fetchone(sql, params)
            return r[0] if r and r[0] is not None else 0

        uid = self.user_id
        kpis = [
            ("My Vehicles",     q("SELECT COUNT(*) FROM VEHICLE WHERE USER_ID=:1", (uid,)),         "🚗", C_ACCENT),
            ("Active Tags",     q("SELECT COUNT(*) FROM TAG WHERE USER_ID=:1 AND STATUS='ACTIVE'", (uid,)), "📡", C_GREEN),
            ("Total Trips",     q("SELECT COUNT(*) FROM TRANSACTION_HISTORY TH JOIN TAG T ON TH.TAG_ID=T.TAG_ID WHERE T.USER_ID=:1", (uid,)), "💸", "#7C3AED"),
            ("Total Paid (Rs)", q("SELECT NVL(SUM(TH.TOTAL_AMOUNT),0) FROM TRANSACTION_HISTORY TH JOIN TAG T ON TH.TAG_ID=T.TAG_ID WHERE T.USER_ID=:1", (uid,)), "💰", C_YELLOW),
        ]

        for i, (title, val, icon, col) in enumerate(kpis):
            card = ctk.CTkFrame(p, fg_color=C_PANEL, corner_radius=12,
                                border_width=2, border_color=col)
            card.grid(row=2, column=i, padx=10, pady=8, sticky="ew")
            ctk.CTkLabel(card, text=icon, font=("Segoe UI Emoji", 26)).pack(pady=(14, 2))
            disp = f"Rs {val:,.0f}" if "Paid" in title else str(val)
            ctk.CTkLabel(card, text=disp,
                         font=("Segoe UI", 20, "bold"),
                         text_color=col).pack()
            ctk.CTkLabel(card, text=title,
                         font=("Segoe UI", 8, "bold"),
                         text_color=C_MUTED).pack(pady=(0, 14))

        r = 3
        # Low balance warning + quick recharge button
        low = db_fetch("""
            SELECT T.TAG_ID, V.PLATE_NUMBER, T.BALANCE
            FROM TAG T JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1 AND T.BALANCE < 500 AND T.STATUS = 'ACTIVE'
        """, (uid,))
        if low:
            warn = ctk.CTkFrame(p, fg_color="#FEF2F2", corner_radius=10,
                                border_width=2, border_color="#FECACA")
            warn.grid(row=r, column=0, columnspan=4, padx=14, pady=(0, 6), sticky="ew")
            warn.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(warn,
                         text=f"⚠  LOW BALANCE  —  {len(low)} tag(s) below Rs 500. Please recharge your tag.",
                         font=("Segoe UI", 10, "bold"),
                         text_color=C_RED).grid(row=0, column=0, pady=10, padx=20, sticky="w")
            ctk.CTkButton(warn, text="💳  Recharge Now",
                          command=lambda: self._tab("request_recharge"),
                          fg_color=C_GREEN, hover_color="#1B5E20",
                          font=("Segoe UI", 10, "bold"),
                          width=150, corner_radius=8,
                          text_color="#FFFFFF").grid(row=0, column=1, padx=14, pady=10, sticky="e")
            r += 1

        # Tag balances
        ctk.CTkLabel(p, text="◆  MY TAG BALANCES",
                     font=FH, text_color=C_ACCENT
                     ).grid(row=r, column=0, columnspan=4,
                            padx=20, pady=(14, 4), sticky="w"); r += 1
        tw, tree = mktable(p, ["TagID","Plate","Vehicle Class","Balance (Rs)","Reserve Bal","Status","Expiry"], 5)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=4, sticky="ew")
        fill(tree, db_fetch("""
            SELECT T.TAG_ID, V.PLATE_NUMBER, VT.VEHICLE_CLASS,
                   T.BALANCE, T.RESERVE_BALANCE, T.STATUS,
                   TO_CHAR(T.EXPIRY_DATE,'DD-Mon-YY')
            FROM TAG T
            JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            JOIN VEHICLE_TYPE VT ON V.TYPE_ID = VT.TYPE_ID
            WHERE T.USER_ID = :1 ORDER BY T.TAG_ID
        """, (uid,))); r += 1

        # Recent transactions
        ctk.CTkLabel(p, text="◆  RECENT TRANSACTIONS",
                     font=FH, text_color=C_ACCENT
                     ).grid(row=r, column=0, columnspan=4,
                            padx=20, pady=(14, 4), sticky="w"); r += 1
        tw2, tree2 = mktable(p, ["TxnID","Plate","Plaza","Distance(Km)","Total(Rs)","Date"], 5)
        tw2.grid(row=r, column=0, columnspan=4, padx=14, pady=4, sticky="ew")
        fill(tree2, db_fetch("""
            SELECT TH.TRANSACTION_ID, V.PLATE_NUMBER,
                   NVL(TP.PLAZA_NAME,'—'),
                   TH.DISTANCE_TRAVELLED, TH.TOTAL_AMOUNT,
                   TO_CHAR(TH.TRANSACTION_DATE,'DD-Mon-YY HH24:MI')
            FROM TRANSACTION_HISTORY TH
            JOIN TAG T ON TH.TAG_ID = T.TAG_ID
            JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            LEFT JOIN TOLL_PLAZA TP ON TH.PLAZA_ID = TP.PLAZA_ID
            WHERE T.USER_ID = :1
            ORDER BY TH.TRANSACTION_ID DESC
            FETCH FIRST 8 ROWS ONLY
        """, (uid,)))

    # ── 1. MY PROFILE ───────────────────────────────────────────
    def _profile(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("👤  MY PROFILE", "Your account details")

        row = db_fetchone("""
            SELECT NAME, CNIC, PHONE, EMAIL, PROVINCE, ADDRESS,
                   EMERGENCY_CONTACT, USERNAME
            FROM USERS WHERE USER_ID = :1
        """, (self.user_id,))

        sec(p, "Account Information", r); r += 1
        info = frm(p)
        info.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        info.grid_columnconfigure((1, 3), weight=1)

        labels = ["Name", "CNIC", "Phone", "Email",
                  "Province", "Address", "Emergency Contact", "Username"]
        values = list(row) if row else ["—"] * 8
        for i, (lbl_text, val) in enumerate(zip(labels, values)):
            ro = i // 2; co = (i % 2) * 2
            ctk.CTkLabel(info, text=lbl_text + ":", font=FL,
                         text_color=C_MUTED, anchor="e"
                         ).grid(row=ro, column=co, padx=(14, 4), pady=6, sticky="e")
            ctk.CTkLabel(info, text=str(val) if val else "—",
                         font=(FM[0], FM[1]), text_color=C_TEXT, anchor="w"
                         ).grid(row=ro, column=co + 1, padx=(0, 14), pady=6, sticky="w")
        r += 1

        sec(p, "Change Password", r); r += 1
        pf = frm(p)
        pf.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        pf.grid_columnconfigure((0, 1, 2, 3), weight=1)
        pw_fields = [
            ("Current Password", "", lambda x: ent(x, "Current password", 210, "●")),
            ("New Password",     "", lambda x: ent(x, "New password",     210, "●")),
            ("Confirm Password", "", lambda x: ent(x, "Confirm new",      210, "●")),
        ]
        pw, pnr = bform(pf, pw_fields, 0, 4)

        def change_password():
            cur_pw = gv(pw["Current Password"])
            new_pw = gv(pw["New Password"])
            conf   = gv(pw["Confirm Password"])
            if not cur_pw or not new_pw:
                return notify("Validation", "All password fields are required.", "error")
            if new_pw != conf:
                return notify("Error", "New passwords do not match.", "error")
            if len(new_pw) < 4:
                return notify("Error", "Password must be at least 4 characters.", "error")
            if not db_fetchone("SELECT USER_ID FROM USERS WHERE USER_ID=:1 AND PASSWORD=:2",
                               (self.user_id, cur_pw)):
                return notify("Error", "Current password is incorrect.", "error")
            if db_exec("UPDATE USERS SET PASSWORD=:1 WHERE USER_ID=:2",
                       (new_pw, self.user_id), commit=True):
                clr(pw)
                notify("Success", "Password changed successfully.", "info")

        btn(pf, "Change Password", change_password, C_YELLOW, 160, "🔑").grid(
            row=pnr, column=0, padx=8, pady=10)

    # ── 2. MY VEHICLES ──────────────────────────────────────────
    def _my_vehicles(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🚗  MY VEHICLES", "Vehicles registered under your account")

        sec(p, "Registered Vehicles", r); r += 1
        tw, tree = mktable(
            p, ["VehicleID","Plate","Model","Company","Color","Type","Driver CNIC","Blacklisted"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        fill(tree, db_fetch("""
            SELECT V.VEHICLE_ID, V.PLATE_NUMBER, NVL(V.MODEL,'—'),
                   NVL(V.COMPANY,'—'), NVL(V.COLOR,'—'),
                   VT.VEHICLE_CLASS, NVL(V.DRIVER_CNIC,'—'), V.IS_BLACKLISTED
            FROM VEHICLE V
            JOIN VEHICLE_TYPE VT ON V.TYPE_ID = VT.TYPE_ID
            WHERE V.USER_ID = :1
            ORDER BY V.VEHICLE_ID DESC
        """, (self.user_id,)))

    # ── 3. MY TAGS ──────────────────────────────────────────────
    def _my_tags(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("📡  MY TAGS", "RFID tags linked to your vehicles")

        sec(p, "Tag Details", r); r += 1
        tw, tree = mktable(
            p, ["TagID","Plate","Balance (Rs)","Reserve Bal","Status","Issue Date","Expiry"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        fill(tree, db_fetch("""
            SELECT T.TAG_ID, V.PLATE_NUMBER, T.BALANCE, T.RESERVE_BALANCE,
                   T.STATUS, TO_CHAR(T.ISSUE_DATE,'DD-Mon-YY'),
                   TO_CHAR(T.EXPIRY_DATE,'DD-Mon-YY')
            FROM TAG T JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1 ORDER BY T.TAG_ID DESC
        """, (self.user_id,)))

    # ── 4. RECHARGE MY TAG (NEW) ────────────────────────────────
    def _request_recharge(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💳  RECHARGE MY TAG", "Top up your RFID tag balance instantly")

        # Fetch this user's active tags only
        tag_rows = db_fetch("""
            SELECT T.TAG_ID, V.PLATE_NUMBER, T.BALANCE
            FROM TAG T JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1 AND T.STATUS = 'ACTIVE'
            ORDER BY T.TAG_ID
        """, (self.user_id,))

        tag_list = [
            f"{x[0]}:{x[1]} (Balance: Rs {x[2]:,.0f})"
            for x in tag_rows
        ] if tag_rows else ["No active tags found"]

        # ── Info banner ──────────────────────────────────────────
        info_f = ctk.CTkFrame(p, fg_color="#EFF6FF", corner_radius=10,
                              border_width=1, border_color="#BFDBFE")
        info_f.grid(row=r, column=0, columnspan=4, padx=14, pady=(0, 8), sticky="ew")
        ctk.CTkLabel(info_f,
                     text="  ℹ  Select your tag, enter an amount, choose a payment method and click Recharge.",
                     font=FS, text_color=C_ACCENT, anchor="w"
                     ).pack(side="left", padx=12, pady=10)
        r += 1

        # ── Recharge form ────────────────────────────────────────
        sec(p, "Recharge Form", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)

        methods = ["Cash", "JazzCash", "EasyPaisa", "Bank Transfer", "Debit Card", "Credit Card"]

        fields = [
            ("My Tag",         "Select",                  lambda x: cmb(x, tag_list)),
            ("Amount (Rs)",    "e.g. 500"),
            ("Payment Method", "Select",                  lambda x: cmb(x, methods)),
            ("Bank / TXN Ref", "Optional reference no."),
        ]
        w, nr = bform(f, fields, 0, 4)

        # Quick-amount buttons row
        ctk.CTkLabel(f, text="Quick Amounts:", font=FL,
                     text_color=C_MUTED, anchor="e"
                     ).grid(row=nr, column=0, padx=(10, 4), pady=6, sticky="e")
        qa_row = ctk.CTkFrame(f, fg_color="transparent")
        qa_row.grid(row=nr, column=1, columnspan=3, sticky="w", padx=(0, 14), pady=6)
        for amt in [200, 500, 1000, 2000, 5000]:
            ctk.CTkButton(qa_row, text=f"Rs {amt:,}",
                          command=lambda a=amt: (
                              w["Amount (Rs)"].delete(0, "end"),
                              w["Amount (Rs)"].insert(0, str(a))
                          ),
                          fg_color="#EFF6FF", hover_color="#DBEAFE",
                          text_color=C_ACCENT, border_color=C_ACCENT,
                          border_width=1, font=FS,
                          width=80, height=30, corner_radius=6
                          ).pack(side="left", padx=4)
        nr += 1

        def submit_recharge():
            tag_raw = gv(w["My Tag"]).split(":")[0]
            amt_s   = gv(w["Amount (Rs)"])
            method  = gv(w["Payment Method"])
            bref    = gv(w["Bank / TXN Ref"])

            if not tag_raw.isdigit():
                return notify("Validation", "Please select a valid tag.", "error")
            if not amt_s:
                return notify("Validation", "Please enter an amount.", "error")
            try:
                amt = float(amt_s)
                if amt <= 0:
                    raise ValueError
            except ValueError:
                return notify("Validation", "Please enter a valid positive amount.", "error")
            if amt < 100:
                return notify("Validation", "Minimum recharge amount is Rs 100.", "error")
            if amt > 50000:
                return notify("Validation", "Maximum recharge amount is Rs 50,000.", "error")

            # Confirm dialog
            if not messagebox.askyesno(
                "Confirm Recharge",
                f"Recharge Tag #{tag_raw}\nAmount: Rs {amt:,.0f}\nMethod: {method}\n\nProceed?"
            ):
                return

            ok = db_exec("BEGIN RECHARGE_TAG(:1,:2,:3,:4); END;",
                         (int(tag_raw), amt, method, bref or None),
                         commit=False)
            if ok:
                clr(w)
                refresh_history()
                notify("Recharge Successful",
                       f"✅  Rs {amt:,.0f} has been added to Tag #{tag_raw}.\n"
                       f"Method: {method}\n"
                       f"Please check your updated balance in My Tags.",
                       "info")

        btn(f, "💳  Recharge Now", submit_recharge, C_GREEN, 180).grid(
            row=nr, column=0, columnspan=2, padx=8, pady=(8, 14), sticky="w")
        r += 1

        # ── Current tag balances (quick reference) ───────────────
        sec(p, "My Current Tag Balances", r); r += 1
        tw_bal, tree_bal = mktable(
            p, ["TagID", "Plate", "Balance (Rs)", "Reserve Bal", "Status", "Expiry"], 5)
        tw_bal.grid(row=r, column=0, columnspan=4, padx=14, pady=4, sticky="ew")
        fill(tree_bal, db_fetch("""
            SELECT T.TAG_ID, V.PLATE_NUMBER, T.BALANCE,
                   T.RESERVE_BALANCE, T.STATUS,
                   TO_CHAR(T.EXPIRY_DATE,'DD-Mon-YY')
            FROM TAG T JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1 ORDER BY T.TAG_ID
        """, (self.user_id,)))
        r += 1

        # ── Recharge history ─────────────────────────────────────
        sec(p, "My Recharge History", r); r += 1
        tw, tree = mktable(
            p, ["RechargeID", "TagID", "Plate", "Amount (Rs)", "Method", "Bank Ref", "Date", "Status"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh_history():
            rows = db_fetch("""
                SELECT AR.RECHARGE_ID, AR.TAG_ID, V.PLATE_NUMBER,
                       AR.RECHARGE_AMOUNT, AR.METHOD, NVL(AR.BANK_REF, '—'),
                       TO_CHAR(AR.RECHARGE_DATE, 'DD-Mon-YY HH24:MI'), AR.STATUS
                FROM ACCOUNT_RECHARGE AR
                JOIN TAG T ON AR.TAG_ID = T.TAG_ID
                JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                WHERE T.USER_ID = :1
                ORDER BY AR.RECHARGE_ID DESC
            """, (self.user_id,))
            fill(tree, rows)
            # Also refresh balance table
            fill(tree_bal, db_fetch("""
                SELECT T.TAG_ID, V.PLATE_NUMBER, T.BALANCE,
                       T.RESERVE_BALANCE, T.STATUS,
                       TO_CHAR(T.EXPIRY_DATE,'DD-Mon-YY')
                FROM TAG T JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                WHERE T.USER_ID = :1 ORDER BY T.TAG_ID
            """, (self.user_id,)))

        btn(p, "↻ Refresh", refresh_history, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh_history()

    # ── 5. MY TRANSACTIONS ──────────────────────────────────────
    def _my_txns(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💸  MY TRANSACTIONS", "All toll deductions for your account")

        sec(p, "Transaction History", r); r += 1
        tw, tree = mktable(
            p, ["TxnID","Plate","Plaza","Entry Terminal","Exit Terminal",
                "Distance(Km)","Rate/Km","Base Toll","Surcharge","Discount","Total(Rs)","Date"], 12)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1

        rows = db_fetch("""
            SELECT TH.TRANSACTION_ID, V.PLATE_NUMBER, NVL(TP.PLAZA_NAME,'—'),
                   NVL(TE.TERMINAL_NAME,'—'), NVL(TX.TERMINAL_NAME,'—'),
                   TH.DISTANCE_TRAVELLED, TH.TOLL_RATE_PER_KM,
                   TH.BASE_TOLL, TH.SURCHARGE, TH.EXEMPTION_DISCOUNT,
                   TH.TOTAL_AMOUNT,
                   TO_CHAR(TH.TRANSACTION_DATE,'DD-Mon-YY HH24:MI')
            FROM TRANSACTION_HISTORY TH
            JOIN TAG T ON TH.TAG_ID = T.TAG_ID
            JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            LEFT JOIN TOLL_PLAZA TP ON TH.PLAZA_ID = TP.PLAZA_ID
            LEFT JOIN TERMINAL TE ON TH.ENTRY_TERMINAL_ID = TE.TERMINAL_ID
            LEFT JOIN TERMINAL TX ON TH.EXIT_TERMINAL_ID = TX.TERMINAL_ID
            WHERE T.USER_ID = :1
            ORDER BY TH.TRANSACTION_ID DESC
        """, (self.user_id,))
        fill(tree, rows)

        total = sum(float(x[10]) for x in rows if x[10]) if rows else 0
        sf = ctk.CTkFrame(p, fg_color="#F0FDF4", corner_radius=10,
                          border_width=1, border_color="#BBF7D0")
        sf.grid(row=r, column=0, columnspan=4, padx=14, pady=8, sticky="ew")
        ctk.CTkLabel(sf,
                     text=f"  Total Trips: {len(rows)}   |   Total Paid: Rs {total:,.2f}",
                     font=("Segoe UI", 11, "bold"),
                     text_color=C_GREEN).pack(pady=10, padx=20, side="left")

    # ── 6. RECHARGE HISTORY ─────────────────────────────────────
    def _my_recharges(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🧾  RECHARGE HISTORY", "All top-ups applied to your tags")

        sec(p, "Recharge Records", r); r += 1
        tw, tree = mktable(
            p, ["RechargeID","TagID","Plate","Amount (Rs)","Method","Bank Ref","Date","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        rows = db_fetch("""
            SELECT AR.RECHARGE_ID, AR.TAG_ID, V.PLATE_NUMBER,
                   AR.RECHARGE_AMOUNT, AR.METHOD, NVL(AR.BANK_REF,'—'),
                   TO_CHAR(AR.RECHARGE_DATE,'DD-Mon-YY HH24:MI'), AR.STATUS
            FROM ACCOUNT_RECHARGE AR
            JOIN TAG T ON AR.TAG_ID = T.TAG_ID
            JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1
            ORDER BY AR.RECHARGE_ID DESC
        """, (self.user_id,))
        fill(tree, rows)

        total = sum(float(x[3]) for x in rows if x[3]) if rows else 0
        sf = ctk.CTkFrame(p, fg_color="#F0FDF4", corner_radius=10,
                          border_width=1, border_color="#BBF7D0")
        sf.grid(row=r + 1, column=0, columnspan=4, padx=14, pady=8, sticky="ew")
        ctk.CTkLabel(sf,
                     text=f"  Total Recharges: {len(rows)}   |   Total Topped Up: Rs {total:,.2f}",
                     font=("Segoe UI", 11, "bold"),
                     text_color=C_GREEN).pack(pady=10, padx=20, side="left")

    # ── 7. PAYMENT HISTORY ──────────────────────────────────────
    def _my_payments(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💵  PAYMENT HISTORY", "All payment records for your tags")

        sec(p, "Payment Records", r); r += 1
        tw, tree = mktable(
            p, ["PaymentID","Plate","Amount (Rs)","Method","Bank Ref","Date","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        fill(tree, db_fetch("""
            SELECT P.PAYMENT_ID, V.PLATE_NUMBER, P.AMOUNT,
                   P.PAYMENT_METHOD, NVL(P.BANK_REF,'—'),
                   TO_CHAR(P.PAYMENT_DATE,'DD-Mon-YY HH24:MI'), P.STATUS
            FROM PAYMENT P
            JOIN TAG T ON P.TAG_ID = T.TAG_ID
            JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1
            ORDER BY P.PAYMENT_ID DESC
        """, (self.user_id,)))

    # ── 8. MY ALERTS ────────────────────────────────────────────
    def _my_alerts(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🔔  MY ALERTS", "System notifications for your tags")

        sec(p, "Notifications", r); r += 1
        tw, tree = mktable(p, ["AlertID","TagID","Plate","Message","Date"], 12)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        rows = db_fetch("""
            SELECT AN.ALERT_ID, AN.TAG_ID, V.PLATE_NUMBER,
                   AN.ALERT_MESSAGE, TO_CHAR(AN.ALERT_DATE,'DD-Mon-YY HH24:MI')
            FROM ALERT_NOTIFICATION AN
            JOIN TAG T ON AN.TAG_ID = T.TAG_ID
            JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            WHERE T.USER_ID = :1
            ORDER BY AN.ALERT_ID DESC
        """, (self.user_id,))
        fill(tree, rows)
        if not rows:
            ctk.CTkLabel(p, text="✅  No alerts — everything looks good.",
                         font=FL, text_color=C_GREEN
                         ).grid(row=r + 1, column=0, columnspan=4, pady=10)

    # ── 9. MY EXEMPTIONS ────────────────────────────────────────
    def _my_exemptions(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🏷  MY EXEMPTIONS", "Toll discount exemptions on your account")

        sec(p, "Active Exemptions", r); r += 1
        tw, tree = mktable(
            p, ["ExemptionID","Plaza","Reason","Discount Type","Discount Value",
                "Start Date","End Date","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        rows = db_fetch("""
            SELECT E.EXEMPTION_ID, NVL(TP.PLAZA_NAME,'All Plazas'),
                   NVL(E.REASON,'—'), NVL(E.DISCOUNT_TYPE,'—'),
                   NVL(TO_CHAR(E.DISCOUNT_VALUE),'—'),
                   TO_CHAR(E.START_DATE,'DD-Mon-YY'),
                   TO_CHAR(E.END_DATE,'DD-Mon-YY'), E.STATUS
            FROM EXEMPTION E
            LEFT JOIN TOLL_PLAZA TP ON E.PLAZA_ID = TP.PLAZA_ID
            WHERE E.USER_ID = :1
            ORDER BY E.EXEMPTION_ID DESC
        """, (self.user_id,))
        fill(tree, rows)
        if not rows:
            ctk.CTkLabel(p, text="No exemptions currently applied to your account.",
                         font=FL, text_color=C_MUTED
                         ).grid(row=r + 1, column=0, columnspan=4, pady=10)

    # ── 10. FEEDBACK ────────────────────────────────────────────
    def _feedback(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💬  FEEDBACK", "Share your experience with us")

        sec(p, "Submit New Feedback", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(f, text="Rating:", font=FL,
                     text_color=C_MUTED, anchor="e"
                     ).grid(row=0, column=0, padx=(14, 4), pady=10, sticky="e")
        rating_var = ctk.StringVar(value="5")
        star_row = ctk.CTkFrame(f, fg_color="transparent")
        star_row.grid(row=0, column=1, columnspan=3, sticky="w", padx=(0, 14), pady=10)
        for val, label in [("1","⭐ 1"),("2","⭐⭐ 2"),("3","⭐⭐⭐ 3"),
                            ("4","⭐⭐⭐⭐ 4"),("5","⭐⭐⭐⭐⭐ 5")]:
            ctk.CTkRadioButton(star_row, text=label, variable=rating_var,
                               value=val, font=FL, text_color=C_TEXT,
                               fg_color=C_ACCENT).pack(side="left", padx=8)

        ctk.CTkLabel(f, text="Comments:", font=FL,
                     text_color=C_MUTED, anchor="e"
                     ).grid(row=1, column=0, padx=(14, 4), pady=8, sticky="ne")
        comments_box = ctk.CTkTextbox(f, height=80, font=FM,
                                      fg_color="#F8FAFC",
                                      border_color=C_BORDER, border_width=1,
                                      text_color=C_TEXT, corner_radius=8)
        comments_box.grid(row=1, column=1, columnspan=3,
                          padx=(0, 14), pady=8, sticky="ew")

        def submit():
            rating = rating_var.get()
            comments = comments_box.get("1.0", "end").strip()
            ok = db_exec(
                "INSERT INTO FEEDBACK(FEEDBACK_ID,USER_ID,RATING,COMMENTS)"
                " VALUES(FEEDBACK_SEQ.NEXTVAL,:1,:2,:3)",
                (self.user_id, int(rating), comments or None), commit=True)
            if ok:
                comments_box.delete("1.0", "end")
                rating_var.set("5")
                refresh()
                notify("Thank You", "Your feedback has been submitted!", "info")

        btn(f, "Submit Feedback", submit, C_GREEN, 170, "💬").grid(
            row=2, column=1, padx=4, pady=(4, 14), sticky="w")
        r += 1

        sec(p, "My Previous Feedback", r); r += 1
        tw, tree = mktable(p, ["FeedbackID","Rating","Comments"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch(
                "SELECT FEEDBACK_ID, RATING, NVL(COMMENTS,'—')"
                " FROM FEEDBACK WHERE USER_ID=:1 ORDER BY FEEDBACK_ID DESC",
                (self.user_id,))
            fill(tree, rows)

        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh()


# ══════════════════════════════════════════════════════════════════
#  ADMIN PORTAL
# ══════════════════════════════════════════════════════════════════
class AdminPortal(ctk.CTk):
    """Full admin portal for system administrators and plaza managers."""

    def __init__(self, user_id, name, role):
        super().__init__()
        self.user_id   = user_id
        self.user_name = name
        self.user_role = role
        self.title(f"ONE TAG ONE NATION  —  Admin Portal  |  {name}  [{role}]")
        self.geometry("1440x860")
        self.minsize(1100, 680)
        self.configure(fg_color=C_BG)
        self._build()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._topbar()
        self._sidebar()
        self._content_area()
        self._dash()

    def _topbar(self):
        bar = ctk.CTkFrame(self, fg_color=C_ADMIN_HEADER,
                           corner_radius=0, height=54)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        ctk.CTkLabel(bar, text="  🛡  ONE TAG ONE NATION  —  Admin Portal",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF"
                     ).grid(row=0, column=0, padx=16, sticky="w")

        ctk.CTkLabel(bar,
                     text=f"  {self.user_name}  |  {self.user_role}  |  ID: {self.user_id}",
                     font=FS, text_color="#F9A8D4"
                     ).grid(row=0, column=1, padx=10)

        pill = "#DCFCE7" if DB_OK else "#FEE2E2"
        ptc  = "#166534" if DB_OK else "#991B1B"
        pt   = f"{'● DB Connected' if DB_OK else '● DB Offline'}  |  {DB_CONFIG['dsn']}"
        ctk.CTkLabel(bar, text=pt, font=FS,
                     text_color=ptc, fg_color=pill,
                     corner_radius=20
                     ).grid(row=0, column=2, padx=10)

        logout_btn = ctk.CTkButton(bar, text="Logout  ⇢",
                                   command=self._logout,
                                   fg_color="#C62828", hover_color="#991B1B",
                                   font=FS, width=100, corner_radius=8)
        logout_btn.grid(row=0, column=3, padx=10)

        self._time_lbl = ctk.CTkLabel(bar, text="", font=FS,
                                      text_color="#CBD5E1")
        self._time_lbl.grid(row=0, column=4, padx=20)
        self._tick()

    def _tick(self):
        self._time_lbl.configure(
            text=datetime.now().strftime("  %a %d %b %Y   %H:%M:%S  "))
        self.after(1000, self._tick)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            app = LoginScreen()
            app.mainloop()

    def _sidebar(self):
        sb = ctk.CTkScrollableFrame(self, fg_color=C_ADMIN_SIDE,
                          corner_radius=0, width=210,
                          scrollbar_button_color="#374151",
                          scrollbar_button_hover_color=C_ADMIN_ACCENT)
        sb.grid(row=1, column=0, sticky="nsew")

        MENU = [
            ("Dashboard",          "📊", self._dash),
            ("── USER MANAGEMENT", "",   None),
            ("  All Users",        "👤", lambda: self._tab("users")),
            ("  Drivers",          "🪪", lambda: self._tab("drivers")),
            ("  Roles",            "🛡", lambda: self._tab("roles")),
            ("── VEHICLES",        "",   None),
            ("  All Vehicles",     "🚗", lambda: self._tab("vehicles")),
            ("  Vehicle Types",    "🏷", lambda: self._tab("vtypes")),
            ("  Blacklist Mgmt",   "🚫", lambda: self._tab("blacklist")),
            ("── TAG & FINANCE",   "",   None),
            ("  All Tags",         "📡", lambda: self._tab("tags")),
            ("  Recharge",         "💳", lambda: self._tab("recharge")),
            ("  Payments",         "💵", lambda: self._tab("payments")),
            ("  Exemptions",       "🏷", lambda: self._tab("exemptions")),
            ("── ROAD NETWORK",    "",   None),
            ("  Motorways",        "🛣",  lambda: self._tab("motorways")),
            ("  Highways",         "🛤",  lambda: self._tab("highways")),
            ("  Highway Updates",  "🔄", lambda: self._tab("hwupdates")),
            ("  Toll Plazas",      "⛽",  lambda: self._tab("plazas")),
            ("  Terminals",        "🚧", lambda: self._tab("terminals")),
            ("  Services",         "🛎", lambda: self._tab("services")),
            ("── OPERATIONS",      "",   None),
            ("  All Transactions", "💸", lambda: self._tab("txns")),
            ("  Employees",        "👷", lambda: self._tab("employees")),
            ("── MONITORING",      "",   None),
            ("  Cameras",          "📷", lambda: self._tab("cameras")),
            ("  Lanes",            "🚦", lambda: self._tab("lanes")),
            ("  Alerts",           "🔔", lambda: self._tab("alerts")),
            ("  All Feedback",     "💬", lambda: self._tab("feedback")),
            ("  Admin Log",        "📋", lambda: self._tab("adminlog")),
            ("  Reports",          "📈", lambda: self._tab("reports")),
        ]

        for text, icon, cmd in MENU:
            if text.startswith("──"):
                ctk.CTkLabel(sb, text=f"  {text}",
                             font=("Segoe UI", 8, "bold"),
                             text_color="#9CA3AF", anchor="w"
                             ).pack(fill="x", padx=6, pady=(10, 2))
            elif cmd is None:
                pass
            else:
                t = f" {icon}  {text.strip()}" if icon else f"  {text.strip()}"
                ctk.CTkButton(sb, text=t,
                              command=lambda c=cmd: c(),
                              fg_color="transparent",
                              hover_color=C_ADMIN_SHOV,
                              text_color="#E5E7EB", anchor="w",
                              font=FL, height=34, corner_radius=8
                              ).pack(fill="x", padx=8, pady=1)

    def _content_area(self):
        self.pane = ctk.CTkScrollableFrame(
            self, fg_color=C_BG, corner_radius=0,
            scrollbar_button_color=C_BORDER,
            scrollbar_button_hover_color=C_ACCENT)
        self.pane.grid(row=1, column=1, sticky="nsew")
        self.pane.grid_columnconfigure(0, weight=1)

    def _reset(self):
        for w in self.pane.winfo_children():
            w.destroy()

    def _title(self, title, sub=""):
        p = self.pane
        ctk.CTkLabel(p, text=title,
                     font=("Segoe UI", 20, "bold"),
                     text_color=C_ACCENT, anchor="w"
                     ).grid(row=0, column=0, columnspan=4,
                            sticky="w", padx=20, pady=(20, 2))
        if sub:
            ctk.CTkLabel(p, text=sub, font=FS,
                         text_color=C_MUTED, anchor="w"
                         ).grid(row=1, column=0, columnspan=4,
                                sticky="w", padx=22, pady=(0, 4))
        db_banner(p, 2)
        return 3

    def _tab(self, key):
        self._reset()
        {
            "users":      self._users,
            "drivers":    self._drivers,
            "roles":      self._roles,
            "vehicles":   self._vehicles,
            "vtypes":     self._vtypes,
            "blacklist":  self._blacklist,
            "tags":       self._tags,
            "recharge":   self._recharge,
            "payments":   self._payments,
            "exemptions": self._exemptions,
            "motorways":  self._motorways,
            "highways":   self._highways,
            "hwupdates":  self._hwupdates,
            "plazas":     self._plazas,
            "terminals":  self._terminals,
            "services":   self._services,
            "txns":       self._txns,
            "employees":  self._employees,
            "cameras":    self._cameras,
            "lanes":      self._lanes,
            "alerts":     self._alerts,
            "feedback":   self._feedback,
            "adminlog":   self._adminlog,
            "reports":    self._reports,
        }[key]()

    # ── ADMIN DASHBOARD ─────────────────────────────────────────
    def _dash(self):
        self._reset()
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(p, text="🛡  SYSTEM DASHBOARD  —  Admin View",
                     font=("Segoe UI", 20, "bold"),
                     text_color=C_ACCENT, anchor="w"
                     ).grid(row=0, column=0, columnspan=4,
                            sticky="w", padx=20, pady=(20, 4))
        db_banner(p, 1)

        def q(sql, fb=0):
            r = db_fetchone(sql)
            return r[0] if r and r[0] is not None else fb

        kpis = [
            ("USERS",         q("SELECT COUNT(*) FROM USERS"),         "👤", C_ACCENT),
            ("VEHICLES",      q("SELECT COUNT(*) FROM VEHICLE"),        "🚗", C_ACT2),
            ("ACTIVE TAGS",   q("SELECT COUNT(*) FROM TAG WHERE STATUS='ACTIVE'"), "📡", C_GREEN),
            ("TRANSACTIONS",  q("SELECT COUNT(*) FROM TRANSACTION_HISTORY"),       "💸", "#7C3AED"),
            ("REVENUE (Rs)",  q("SELECT NVL(SUM(TOTAL_AMOUNT),0) FROM TRANSACTION_HISTORY"), "💰", C_YELLOW),
            ("LOW BALANCE",   q("SELECT COUNT(*) FROM TAG WHERE BALANCE<500"),     "⚠",  C_RED),
            ("TOLL PLAZAS",   q("SELECT COUNT(*) FROM TOLL_PLAZA"),    "⛽", C_ACCENT),
            ("EMPLOYEES",     q("SELECT COUNT(*) FROM EMPLOYEE"),      "👷", C_MUTED),
            ("BLACKLISTED",   q("SELECT COUNT(*) FROM VEHICLE WHERE IS_BLACKLISTED='Y'"), "🚫", C_RED),
            ("PENDING ALERTS",q("SELECT COUNT(*) FROM ALERT_NOTIFICATION WHERE TRUNC(ALERT_DATE)=TRUNC(SYSDATE)"), "🔔", C_YELLOW),
            ("ACTIVE CAMERAS",q("SELECT COUNT(*) FROM CAMERA_SYSTEM WHERE STATUS='ACTIVE'"), "📷", C_GREEN),
            ("OPEN LANES",    q("SELECT COUNT(*) FROM LANE WHERE STATUS='OPEN'"),  "🚦", C_ACCENT),
        ]

        for i, (title, val, icon, col) in enumerate(kpis):
            card = ctk.CTkFrame(p, fg_color=C_PANEL, corner_radius=12,
                                border_width=2, border_color=col)
            card.grid(row=2 + i // 4, column=i % 4,
                      padx=10, pady=8, sticky="ew")
            ctk.CTkLabel(card, text=icon,
                         font=("Segoe UI Emoji", 24)).pack(pady=(14, 2))
            disp = f"Rs {val:,.0f}" if "REVENUE" in title else str(val)
            ctk.CTkLabel(card, text=disp,
                         font=("Segoe UI", 20, "bold"),
                         text_color=col).pack()
            ctk.CTkLabel(card, text=title,
                         font=("Segoe UI", 8, "bold"),
                         text_color=C_MUTED).pack(pady=(0, 14))

        r = 5
        ctk.CTkLabel(p, text="◆  TOLL CALCULATION FORMULA",
                     font=FH, text_color=C_ACCENT
                     ).grid(row=r, column=0, columnspan=4,
                            padx=20, pady=(16, 4), sticky="w")
        r += 1
        formula_frm = ctk.CTkFrame(p, fg_color="#EFF6FF", corner_radius=10,
                                   border_width=2, border_color="#BFDBFE")
        formula_frm.grid(row=r, column=0, columnspan=4,
                         padx=14, pady=4, sticky="ew")
        formula_frm.grid_columnconfigure((0,1,2,3), weight=1)
        formulas = [
            ("Distance",   "Exit Mile No. − Entry Mile No.",    C_ACCENT),
            ("Base Toll",  "Distance × Vehicle Rate/Km",        C_ACT2),
            ("Surcharge",  "From Highway Update table",         C_YELLOW),
            ("Final Toll", "Base Toll + Surcharge − Exemption", C_GREEN),
        ]
        for i, (label, formula, col) in enumerate(formulas):
            cf = ctk.CTkFrame(formula_frm, fg_color="#FFFFFF", corner_radius=8,
                              border_width=1, border_color=col)
            cf.grid(row=0, column=i, padx=8, pady=12, sticky="ew")
            ctk.CTkLabel(cf, text=label, font=("Segoe UI", 8, "bold"),
                         text_color=C_MUTED).pack(pady=(10,2), padx=10)
            ctk.CTkLabel(cf, text=formula, font=("Segoe UI", 10, "bold"),
                         text_color=col, justify="center",
                         wraplength=180).pack(pady=(0,10), padx=10)
        r += 1

        ctk.CTkLabel(p, text="◆  RECENT TRANSACTIONS",
                     font=FH, text_color=C_ACCENT
                     ).grid(row=r, column=0, columnspan=4,
                            padx=20, pady=(16, 4), sticky="w")
        r += 1
        tw, tree = mktable(
            p, ["TxnID","TagID","Plate","PlazaID","Distance(Km)","Amount(Rs)","Date"], 6)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=4, sticky="ew")
        rows = db_fetch("""
            SELECT TH.TRANSACTION_ID, TH.TAG_ID, V.PLATE_NUMBER,
                   TH.PLAZA_ID, TH.DISTANCE_TRAVELLED,
                   TH.TOTAL_AMOUNT,
                   TO_CHAR(TH.TRANSACTION_DATE,'DD-Mon-YY HH24:MI')
            FROM TRANSACTION_HISTORY TH
            LEFT JOIN TAG T ON TH.TAG_ID = T.TAG_ID
            LEFT JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            ORDER BY TH.TRANSACTION_ID DESC
            FETCH FIRST 10 ROWS ONLY
        """)
        fill(tree, rows)

    # ══════════════════════════════════════════════════════════
    #  ADMIN SECTIONS — FULL CRUD
    # ══════════════════════════════════════════════════════════

    # ── 1. ALL USERS ────────────────────────────────────────────
    def _users(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("👤  USER MANAGEMENT", "Add, edit and manage all system users")

        sec(p, "Add New User", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Name",              "Full Name"),
            ("CNIC",              "XXXXX-XXXXXXX-X"),
            ("Phone",             "03XX-XXXXXXX"),
            ("Email",             "user@email.com"),
            ("Province",          "e.g. Punjab"),
            ("Address",           "Street, City"),
            ("Emergency Contact", "03XX-XXXXXXX"),
            ("Username",          "login name"),
            ("Password",          "password"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "User List", r + 1); r += 2
        tw, tree = mktable(
            p, ["UserID","Name","CNIC","Phone","Province","Email","Active","Username"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch(
                "SELECT USER_ID,NAME,CNIC,PHONE,PROVINCE,EMAIL,IS_ACTIVE,USERNAME"
                " FROM USERS ORDER BY USER_ID DESC")
            fill(tree, rows)

        def add():
            vals = {k: gv(v) for k, v in w.items()}
            if not vals["Name"] or not vals["CNIC"]:
                return notify("Validation", "Name and CNIC required", "error")
            ok = db_exec(
                "INSERT INTO USERS(USER_ID,NAME,CNIC,PHONE,EMAIL,PROVINCE,ADDRESS,"
                "EMERGENCY_CONTACT,USERNAME,PASSWORD)"
                " VALUES(USER_SEQ.NEXTVAL,:1,:2,:3,:4,:5,:6,:7,:8,:9)",
                (vals["Name"], vals["CNIC"], vals["Phone"], vals["Email"],
                 vals["Province"], vals["Address"], vals["Emergency Contact"],
                 vals["Username"], vals["Password"]),
                commit=True)
            if ok:
                db_exec("INSERT INTO ADMIN_LOG(LOG_ID,ADMIN_USER_ID,ACTION_TYPE,ACTION_DETAIL,LOG_DATE)"
                        " VALUES(ADMIN_LOG_SEQ.NEXTVAL,:1,'ADD_USER','Added user: '||:2,SYSTIMESTAMP)",
                        (self.user_id, vals["Name"]), commit=True)
                refresh(); clr(w)
                notify("Success", "User added", "info")

        def toggle_active():
            sel = tree.selection()
            if not sel:
                return notify("Select", "Select a user first", "warning")
            uid = tree.item(sel[0])["values"][0]
            cur = tree.item(sel[0])["values"][6]
            new = "N" if cur == "Y" else "Y"
            db_exec("UPDATE USERS SET IS_ACTIVE=:1 WHERE USER_ID=:2",
                    (new, uid), commit=True)
            db_exec("INSERT INTO ADMIN_LOG(LOG_ID,ADMIN_USER_ID,ACTION_TYPE,ACTION_DETAIL,LOG_DATE)"
                    " VALUES(ADMIN_LOG_SEQ.NEXTVAL,:1,'TOGGLE_USER','UserID '||:2||' set active='||:3,SYSTIMESTAMP)",
                    (self.user_id, uid, new), commit=True)
            refresh()

        btn(f, "Add User", add, C_GREEN, 130, "👤").grid(
            row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(
            row=r + 1, column=2, padx=14, pady=6, sticky="e")
        btn(p, "Toggle Active", toggle_active, C_YELLOW, 140).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 2. DRIVERS ──────────────────────────────────────────────
    def _drivers(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🪪  DRIVER MANAGEMENT", "Register and manage drivers")

        sec(p, "Add Driver", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("CNIC",           "XXXXX-XXXXXXX-X"),
            ("Name",           "Full Name"),
            ("License No",     "LIC-XXXX"),
            ("Phone",          "03XX-XXXXXXX"),
            ("License Expiry", "YYYY-MM-DD"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Driver List", r + 1); r += 2
        tw, tree = mktable(p, ["CNIC","Name","LicenseNo","Phone","Expiry"], 9)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch(
                "SELECT DRIVER_CNIC,DRIVER_NAME,LICENSE_NO,DRIVER_PHONE,"
                "TO_CHAR(LICENSE_EXPIRY,'YYYY-MM-DD') FROM DRIVER ORDER BY DRIVER_NAME")
            fill(tree, rows)

        def add():
            cnic = gv(w["CNIC"])
            if not cnic:
                return notify("Validation", "CNIC required", "error")
            ok = db_exec(
                "INSERT INTO DRIVER(DRIVER_CNIC,DRIVER_NAME,LICENSE_NO,DRIVER_PHONE,LICENSE_EXPIRY)"
                " VALUES(:1,:2,:3,:4,TO_DATE(:5,'YYYY-MM-DD'))",
                (cnic, gv(w["Name"]), gv(w["License No"]),
                 gv(w["Phone"]), gv(w["License Expiry"])),
                commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Driver added", "info")

        btn(f, "Add Driver", add, C_GREEN, 130, "🪪").grid(
            row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 3. ROLES ────────────────────────────────────────────────
    def _roles(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🛡  ROLE MANAGEMENT", "Manage user roles and assignments")

        sec(p, "Roles", r); r += 1
        tw, tree = mktable(p, ["RoleID","Role Name","Description"], 5)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        rows = db_fetch("SELECT ROLE_ID,ROLE_NAME,DESCRIPTION FROM ROLE ORDER BY ROLE_ID")
        fill(tree, rows)
        r += 1

        sec(p, "Assign Role to User", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        uids  = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT USER_ID,NAME FROM USERS ORDER BY USER_ID")]
        roles = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT ROLE_ID,ROLE_NAME FROM ROLE ORDER BY ROLE_ID")]
        fields = [
            ("User",  "Select", lambda x: cmb(x, uids  or ["—"])),
            ("Role",  "Select", lambda x: cmb(x, roles or ["—"])),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Current Role Assignments", r + 1); r += 2
        tw2, tree2 = mktable(p, ["UserRoleID","UserID","Name","Role","AssignedDate"], 8)
        tw2.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh2():
            rows2 = db_fetch("""
                SELECT UR.USER_ROLE_ID, U.USER_ID, U.NAME, R.ROLE_NAME,
                       TO_CHAR(UR.ASSIGNED_DATE,'YYYY-MM-DD')
                FROM USER_ROLE UR
                JOIN USERS U ON UR.USER_ID = U.USER_ID
                JOIN ROLE R ON UR.ROLE_ID = R.ROLE_ID
                ORDER BY UR.USER_ROLE_ID DESC
            """)
            fill(tree2, rows2)

        def assign():
            u_raw = gv(w["User"]).split(":")[0]
            r_raw = gv(w["Role"]).split(":")[0]
            if not u_raw.isdigit() or not r_raw.isdigit():
                return notify("Validation", "Select both user and role", "error")
            ok = db_exec(
                "INSERT INTO USER_ROLE(USER_ROLE_ID,USER_ID,ROLE_ID,ASSIGNED_DATE)"
                " VALUES(USER_ROLE_SEQ.NEXTVAL,:1,:2,SYSDATE)",
                (int(u_raw), int(r_raw)), commit=True)
            if ok:
                refresh2(); clr(w)
                notify("Success", "Role assigned", "info")

        btn(f, "Assign Role", assign, C_ACCENT, 140, "🛡").grid(
            row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh2, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh2()

    # ── 4. ALL VEHICLES ─────────────────────────────────────────
    def _vehicles(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🚗  VEHICLE MANAGEMENT", "All registered vehicles")

        sec(p, "Register Vehicle", r); r += 1
        uids  = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT USER_ID,NAME FROM USERS ORDER BY USER_ID")]
        types = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT TYPE_ID,VEHICLE_CLASS FROM VEHICLE_TYPE ORDER BY TYPE_ID")]
        drvs  = [x[0] for x in db_fetch("SELECT DRIVER_CNIC FROM DRIVER ORDER BY DRIVER_NAME")]

        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("User",         "Select", lambda x: cmb(x, uids  or ["—"])),
            ("Vehicle Type", "Select", lambda x: cmb(x, types or ["1:Car"])),
            ("Driver CNIC",  "Select", lambda x: cmb(x, drvs  or ["—"])),
            ("Plate Number", "e.g. LEA-1234"),
            ("Model",        "e.g. Corolla"),
            ("Company",      "e.g. Toyota"),
            ("Color",        "e.g. White"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Vehicle Registry", r + 1); r += 2
        tw, tree = mktable(
            p, ["VehicleID","Owner","DriverCNIC","Type","Plate","Model","Company","Blacklisted"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT V.VEHICLE_ID, U.NAME, V.DRIVER_CNIC,
                       VT.VEHICLE_CLASS, V.PLATE_NUMBER, V.MODEL,
                       V.COMPANY, V.IS_BLACKLISTED
                FROM VEHICLE V
                JOIN USERS U ON V.USER_ID = U.USER_ID
                JOIN VEHICLE_TYPE VT ON V.TYPE_ID = VT.TYPE_ID
                ORDER BY V.VEHICLE_ID DESC
            """)
            fill(tree, rows)

        def add():
            u_raw = gv(w["User"]).split(":")[0]
            t_raw = gv(w["Vehicle Type"]).split(":")[0]
            drv   = gv(w["Driver CNIC"])
            plate = gv(w["Plate Number"])
            if not plate or not u_raw.isdigit():
                return notify("Validation", "User and Plate required", "error")
            ok = db_exec("""
                INSERT INTO VEHICLE(VEHICLE_ID,USER_ID,DRIVER_CNIC,TYPE_ID,
                    PLATE_NUMBER,MODEL,COMPANY,COLOR)
                VALUES(VEHICLE_SEQ.NEXTVAL,:1,:2,:3,:4,:5,:6,:7)
            """, (int(u_raw), drv if drv and drv != "—" else None,
                  int(t_raw) if t_raw.isdigit() else 1,
                  plate, gv(w["Model"]), gv(w["Company"]), gv(w["Color"])),
                commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Vehicle registered", "info")

        btn(f, "Register Vehicle", add, C_GREEN, 160, "🚗").grid(
            row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 5. VEHICLE TYPES ────────────────────────────────────────
    def _vtypes(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🏷  VEHICLE TYPES", "Car / Bus / Truck toll rates per km")

        sec(p, "Add/Edit Vehicle Type", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Vehicle Class", "e.g. Car"),
            ("Rate Per Km",   "e.g. 5.00"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Vehicle Type List", r + 1); r += 2
        tw, tree = mktable(p, ["TypeID","Vehicle Class","Toll Rate/Km (Rs)"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("SELECT TYPE_ID,VEHICLE_CLASS,TOLL_RATE_PER_KM FROM VEHICLE_TYPE ORDER BY TYPE_ID")
            fill(tree, rows)

        def add():
            cls = gv(w["Vehicle Class"])
            rate = gv(w["Rate Per Km"])
            if not cls or not rate:
                return notify("Validation", "All fields required", "error")
            ok = db_exec(
                "INSERT INTO VEHICLE_TYPE(TYPE_ID,VEHICLE_CLASS,TOLL_RATE_PER_KM)"
                " VALUES(VTYPE_SEQ.NEXTVAL,:1,:2)",
                (cls, float(rate)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Vehicle type added", "info")

        btn(f, "Add Type", add, C_GREEN, 130, "🏷").grid(
            row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 6. BLACKLIST MANAGEMENT ─────────────────────────────────
    def _blacklist(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🚫  BLACKLIST MANAGEMENT", "Flag or clear blacklisted vehicles")

        sec(p, "Blacklisted Vehicles", r); r += 1
        tw, tree = mktable(
            p, ["VehicleID","Plate","Owner","Model","Type","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1

        def refresh():
            rows = db_fetch("""
                SELECT V.VEHICLE_ID, V.PLATE_NUMBER, U.NAME,
                       V.MODEL, VT.VEHICLE_CLASS, V.IS_BLACKLISTED
                FROM VEHICLE V
                JOIN USERS U ON V.USER_ID = U.USER_ID
                JOIN VEHICLE_TYPE VT ON V.TYPE_ID = VT.TYPE_ID
                WHERE V.IS_BLACKLISTED = 'Y'
                ORDER BY V.VEHICLE_ID DESC
            """)
            fill(tree, rows)

        def blacklist_by_plate():
            plate = gv(w_plate)
            if not plate:
                return notify("Validation", "Enter a plate number", "error")
            ok = db_exec("UPDATE VEHICLE SET IS_BLACKLISTED='Y' WHERE PLATE_NUMBER=:1",
                         (plate,), commit=True)
            if ok:
                db_exec("INSERT INTO ADMIN_LOG(LOG_ID,ADMIN_USER_ID,ACTION_TYPE,ACTION_DETAIL,LOG_DATE)"
                        " VALUES(ADMIN_LOG_SEQ.NEXTVAL,:1,'BLACKLIST','Blacklisted plate: '||:2,SYSTIMESTAMP)",
                        (self.user_id, plate), commit=True)
                refresh()
                notify("Done", f"Vehicle {plate} blacklisted", "warning")

        def clear_selected():
            sel = tree.selection()
            if not sel:
                return notify("Select", "Select a vehicle to clear", "warning")
            vid = tree.item(sel[0])["values"][0]
            plate = tree.item(sel[0])["values"][1]
            db_exec("UPDATE VEHICLE SET IS_BLACKLISTED='N' WHERE VEHICLE_ID=:1",
                    (vid,), commit=True)
            db_exec("INSERT INTO ADMIN_LOG(LOG_ID,ADMIN_USER_ID,ACTION_TYPE,ACTION_DETAIL,LOG_DATE)"
                    " VALUES(ADMIN_LOG_SEQ.NEXTVAL,:1,'CLEAR_BLACKLIST','Cleared blacklist for VehicleID '||:2,SYSTIMESTAMP)",
                    (self.user_id, vid), commit=True)
            refresh()
            notify("Done", f"Blacklist cleared for {plate}", "info")

        cf = frm(p)
        cf.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        ctk.CTkLabel(cf, text="Plate Number:", font=FL, text_color=C_MUTED).grid(
            row=0, column=0, padx=10, pady=10, sticky="e")
        w_plate = ent(cf, "e.g. LEA-1234")
        w_plate.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        btn(cf, "Blacklist Vehicle", blacklist_by_plate, C_RED, 160, "🚫").grid(
            row=0, column=2, padx=10, pady=10)
        btn(cf, "Clear Selected", clear_selected, C_GREEN, 140, "✅").grid(
            row=0, column=3, padx=10, pady=10)

        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(
            row=r + 1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 7. ALL TAGS ─────────────────────────────────────────────
    def _tags(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("📡  TAG MANAGEMENT", "Issue and manage RFID tags")

        sec(p, "Issue New Tag", r); r += 1
        uids = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT USER_ID,NAME FROM USERS ORDER BY USER_ID")]
        vehs = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT VEHICLE_ID,PLATE_NUMBER FROM VEHICLE ORDER BY VEHICLE_ID")]

        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("User",            "Select",   lambda x: cmb(x, uids or ["—"])),
            ("Vehicle",         "Select",   lambda x: cmb(x, vehs or ["—"])),
            ("Initial Balance", "e.g. 500"),
            ("Reserve Balance", "e.g. 100"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "All Tags", r + 1); r += 2
        tw, tree = mktable(
            p, ["TagID","Owner","Plate","Balance","Reserve","Status","IssueDate","Expiry"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT T.TAG_ID, U.NAME, V.PLATE_NUMBER,
                       T.BALANCE, T.RESERVE_BALANCE, T.STATUS,
                       TO_CHAR(T.ISSUE_DATE,'DD-Mon-YY'),
                       TO_CHAR(T.EXPIRY_DATE,'DD-Mon-YY')
                FROM TAG T
                JOIN USERS U ON T.USER_ID = U.USER_ID
                JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                ORDER BY T.TAG_ID DESC
            """)
            fill(tree, rows)

        def issue():
            u_raw = gv(w["User"]).split(":")[0]
            v_raw = gv(w["Vehicle"]).split(":")[0]
            bal   = gv(w["Initial Balance"]) or "0"
            res   = gv(w["Reserve Balance"]) or "0"
            if not u_raw.isdigit() or not v_raw.isdigit():
                return notify("Validation", "Select user and vehicle", "error")
            ok = db_exec("""
                INSERT INTO TAG(TAG_ID,USER_ID,VEHICLE_ID,BALANCE,RESERVE_BALANCE,
                    STATUS,ISSUE_DATE,EXPIRY_DATE)
                VALUES(TAG_SEQ.NEXTVAL,:1,:2,:3,:4,'ACTIVE',SYSDATE,ADD_MONTHS(SYSDATE,12))
            """, (int(u_raw), int(v_raw), float(bal), float(res)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Tag issued", "info")

        def suspend():
            sel = tree.selection()
            if not sel: return notify("Select","Select a tag","warning")
            tid = tree.item(sel[0])["values"][0]
            cur = tree.item(sel[0])["values"][5]
            new = "SUSPENDED" if cur == "ACTIVE" else "ACTIVE"
            db_exec("UPDATE TAG SET STATUS=:1 WHERE TAG_ID=:2", (new, tid), commit=True)
            refresh()

        btn(f, "Issue Tag", issue, C_GREEN, 130, "📡").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=2, padx=14, pady=6, sticky="e")
        btn(p, "Suspend/Activate", suspend, C_YELLOW, 160).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 8. RECHARGE (ADMIN) ─────────────────────────────────────
    def _recharge(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💳  ACCOUNT RECHARGE", "Recharge any tag balance")

        tags = [f"{x[0]}:{x[1]} (Rs{x[2]:,.0f})" for x in
                db_fetch("""
                    SELECT T.TAG_ID, V.PLATE_NUMBER, T.BALANCE
                    FROM TAG T JOIN VEHICLE V ON T.VEHICLE_ID=V.VEHICLE_ID
                    WHERE T.STATUS='ACTIVE' ORDER BY T.TAG_ID
                """)]
        sec(p, "Process Recharge", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        methods = ["Cash","JazzCash","EasyPaisa","Bank Transfer","Debit Card","Credit Card"]
        fields = [
            ("Tag",     "Select", lambda x: cmb(x, tags or ["—"])),
            ("Amount (Rs)", "e.g. 500"),
            ("Method",  "Select", lambda x: cmb(x, methods)),
            ("Bank Ref","TXN-XXXXXX"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Recharge History", r + 1); r += 2
        tw, tree = mktable(
            p, ["RechargeID","TagID","Plate","Amount(Rs)","Method","BankRef","Date","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT AR.RECHARGE_ID, AR.TAG_ID, V.PLATE_NUMBER,
                       AR.RECHARGE_AMOUNT, AR.METHOD, NVL(AR.BANK_REF,'—'),
                       TO_CHAR(AR.RECHARGE_DATE,'DD-Mon-YY HH24:MI'), AR.STATUS
                FROM ACCOUNT_RECHARGE AR
                JOIN TAG T ON AR.TAG_ID = T.TAG_ID
                JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                ORDER BY AR.RECHARGE_ID DESC
            """)
            fill(tree, rows)

        def recharge():
            tag_raw = gv(w["Tag"]).split(":")[0]
            amt_s   = gv(w["Amount (Rs)"])
            method  = gv(w["Method"])
            bref    = gv(w["Bank Ref"])
            if not tag_raw.isdigit() or not amt_s:
                return notify("Validation", "Select tag and enter amount", "error")
            ok = db_exec("BEGIN RECHARGE_TAG(:1,:2,:3,:4); END;",
                         (int(tag_raw), float(amt_s), method, bref or None),
                         commit=False)
            if ok:
                refresh(); clr(w)
                notify("Success", f"Rs {float(amt_s):,.0f} recharged", "info")

        btn(f, "Recharge", recharge, C_GREEN, 130, "💳").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 9. PAYMENTS ─────────────────────────────────────────────
    def _payments(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💵  PAYMENTS", "All payment records")

        sec(p, "Record Payment", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        methods = ["Cash","JazzCash","EasyPaisa","Bank Transfer"]
        fields = [
            ("Tag ID",   "Select", lambda x: cmb(x, [str(x[0]) for x in db_fetch("SELECT TAG_ID FROM TAG ORDER BY TAG_ID")] or ["—"])),
            ("Amount",   "e.g. 200"),
            ("Method",   "Select", lambda x: cmb(x, methods)),
            ("Bank Ref", "optional"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Payment History", r + 1); r += 2
        tw, tree = mktable(
            p, ["PaymentID","TagID","Plate","Amount(Rs)","Method","BankRef","Date","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT P.PAYMENT_ID, P.TAG_ID, V.PLATE_NUMBER,
                       P.AMOUNT, P.PAYMENT_METHOD, NVL(P.BANK_REF,'—'),
                       TO_CHAR(P.PAYMENT_DATE,'DD-Mon-YY'), P.STATUS
                FROM PAYMENT P
                JOIN TAG T ON P.TAG_ID = T.TAG_ID
                JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                ORDER BY P.PAYMENT_ID DESC
            """)
            fill(tree, rows)

        def add():
            tid = gv(w["Tag ID"])
            amt = gv(w["Amount"])
            if not tid or not amt:
                return notify("Validation", "Tag and amount required", "error")
            ok = db_exec(
                "INSERT INTO PAYMENT(PAYMENT_ID,TAG_ID,AMOUNT,PAYMENT_METHOD,BANK_REF,STATUS)"
                " VALUES(PAYMENT_SEQ.NEXTVAL,:1,:2,:3,:4,'SUCCESS')",
                (int(tid), float(amt), gv(w["Method"]), gv(w["Bank Ref"]) or None),
                commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Payment recorded", "info")

        btn(f, "Record Payment", add, C_GREEN, 150, "💵").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 10. EXEMPTIONS ──────────────────────────────────────────
    def _exemptions(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🏷  EXEMPTIONS", "Manage toll discount exemptions")

        uids   = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT USER_ID,NAME FROM USERS ORDER BY USER_ID")]
        plazas = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT PLAZA_ID,PLAZA_NAME FROM TOLL_PLAZA ORDER BY PLAZA_ID")]

        sec(p, "Add Exemption", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        dtype = ["PERCENT","FIXED"]
        fields = [
            ("User",           "Select",          lambda x: cmb(x, uids   or ["—"])),
            ("Plaza (opt)",    "Select",          lambda x: cmb(x, ["ALL"] + (plazas or []))),
            ("Reason",         "e.g. Government"),
            ("Discount Type",  "Select",          lambda x: cmb(x, dtype)),
            ("Discount Value", "e.g. 50"),
            ("Start Date",     "YYYY-MM-DD"),
            ("End Date",       "YYYY-MM-DD"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Exemption List", r + 1); r += 2
        tw, tree = mktable(
            p, ["ExemptID","User","Plaza","Reason","Type","Value","Start","End","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT E.EXEMPTION_ID, U.NAME, NVL(TP.PLAZA_NAME,'All'),
                       NVL(E.REASON,'—'), NVL(E.DISCOUNT_TYPE,'—'),
                       NVL(TO_CHAR(E.DISCOUNT_VALUE),'—'),
                       TO_CHAR(E.START_DATE,'YYYY-MM-DD'),
                       TO_CHAR(E.END_DATE,'YYYY-MM-DD'), E.STATUS
                FROM EXEMPTION E
                JOIN USERS U ON E.USER_ID = U.USER_ID
                LEFT JOIN TOLL_PLAZA TP ON E.PLAZA_ID = TP.PLAZA_ID
                ORDER BY E.EXEMPTION_ID DESC
            """)
            fill(tree, rows)

        def add():
            u_raw = gv(w["User"]).split(":")[0]
            p_raw = gv(w["Plaza (opt)"]).split(":")[0]
            if not u_raw.isdigit():
                return notify("Validation", "Select a user", "error")
            ok = db_exec("""
                INSERT INTO EXEMPTION(EXEMPTION_ID,USER_ID,PLAZA_ID,REASON,
                    DISCOUNT_TYPE,DISCOUNT_VALUE,START_DATE,END_DATE,STATUS)
                VALUES(EXEMPTION_SEQ.NEXTVAL,:1,:2,:3,:4,:5,
                    TO_DATE(:6,'YYYY-MM-DD'),TO_DATE(:7,'YYYY-MM-DD'),'ACTIVE')
            """, (int(u_raw),
                  int(p_raw) if p_raw.isdigit() else None,
                  gv(w["Reason"]), gv(w["Discount Type"]),
                  float(gv(w["Discount Value"]) or 0),
                  gv(w["Start Date"]), gv(w["End Date"])),
                commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Exemption added", "info")

        btn(f, "Add Exemption", add, C_GREEN, 150, "🏷").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 11. MOTORWAYS ───────────────────────────────────────────
    def _motorways(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🛣  MOTORWAY MANAGEMENT", "National motorway network")

        sec(p, "Add Motorway", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Motorway Name",    "e.g. M-2"),
            ("Start City",       "e.g. Lahore"),
            ("End City",         "e.g. Islamabad"),
            ("Total Distance Km","e.g. 367"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Motorway List", r + 1); r += 2
        tw, tree = mktable(p, ["MotorwayID","Name","Start","End","Distance(Km)"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("SELECT MOTORWAY_ID,MOTORWAY_NAME,START_CITY,END_CITY,TOTAL_DISTANCE_KM FROM MOTORWAY ORDER BY MOTORWAY_ID")
            fill(tree, rows)

        def add():
            name = gv(w["Motorway Name"])
            if not name:
                return notify("Validation", "Name required", "error")
            ok = db_exec(
                "INSERT INTO MOTORWAY(MOTORWAY_ID,MOTORWAY_NAME,START_CITY,END_CITY,TOTAL_DISTANCE_KM)"
                " VALUES(MOTORWAY_SEQ.NEXTVAL,:1,:2,:3,:4)",
                (name, gv(w["Start City"]), gv(w["End City"]),
                 float(gv(w["Total Distance Km"]) or 0)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Motorway added", "info")

        btn(f, "Add Motorway", add, C_GREEN, 140, "🛣").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 12. HIGHWAYS ────────────────────────────────────────────
    def _highways(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🛤  HIGHWAY MANAGEMENT", "Highway sections per motorway")

        mways = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT MOTORWAY_ID,MOTORWAY_NAME FROM MOTORWAY ORDER BY MOTORWAY_ID")]
        sec(p, "Add Highway", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        dirs = ["BOTH","NORTHBOUND","SOUTHBOUND","EASTBOUND","WESTBOUND"]
        fields = [
            ("Motorway",      "Select",     lambda x: cmb(x, mways or ["—"])),
            ("Highway Name",  "e.g. M-2 Section A"),
            ("Section Name",  "e.g. Lahore-Sheikhupura"),
            ("Direction",     "Select",     lambda x: cmb(x, dirs)),
            ("Start Location","e.g. Lahore"),
            ("End Location",  "e.g. Pindi Bhattian"),
            ("Distance (Km)", "e.g. 112"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Highway List", r + 1); r += 2
        tw, tree = mktable(p, ["HwyID","Motorway","Name","Section","Direction","Distance"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT H.HIGHWAY_ID,M.MOTORWAY_NAME,H.HIGHWAY_NAME,
                       NVL(H.SECTION_NAME,'—'),NVL(H.DIRECTION,'—'),H.TOTAL_DISTANCE
                FROM HIGHWAY H JOIN MOTORWAY M ON H.MOTORWAY_ID=M.MOTORWAY_ID
                ORDER BY H.HIGHWAY_ID
            """)
            fill(tree, rows)

        def add():
            m_raw = gv(w["Motorway"]).split(":")[0]
            name  = gv(w["Highway Name"])
            if not m_raw.isdigit() or not name:
                return notify("Validation", "Motorway and name required", "error")
            ok = db_exec("""
                INSERT INTO HIGHWAY(HIGHWAY_ID,MOTORWAY_ID,HIGHWAY_NAME,SECTION_NAME,
                    DIRECTION,START_LOCATION,END_LOCATION,TOTAL_DISTANCE)
                VALUES(HWY_SEQ.NEXTVAL,:1,:2,:3,:4,:5,:6,:7)
            """, (int(m_raw), name, gv(w["Section Name"]), gv(w["Direction"]),
                  gv(w["Start Location"]), gv(w["End Location"]),
                  float(gv(w["Distance (Km)"]) or 0)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Highway added", "info")

        btn(f, "Add Highway", add, C_GREEN, 140, "🛤").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 13. HIGHWAY UPDATES ─────────────────────────────────────
    def _hwupdates(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🔄  HIGHWAY UPDATES", "Surcharge updates for highways")

        hways = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT HIGHWAY_ID,HIGHWAY_NAME FROM HIGHWAY ORDER BY HIGHWAY_ID")]
        sec(p, "Add Highway Surcharge Update", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Highway",       "Select", lambda x: cmb(x, hways or ["—"])),
            ("Surcharge (Rs)","e.g. 50"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Highway Update Log", r + 1); r += 2
        tw, tree = mktable(p, ["UpdateID","Highway","Surcharge(Rs)","Date"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT HU.UPDATE_ID,H.HIGHWAY_NAME,HU.SURCHARGE,
                       TO_CHAR(HU.UPDATE_DATE,'DD-Mon-YY HH24:MI')
                FROM HIGHWAY_UPDATE HU JOIN HIGHWAY H ON HU.HIGHWAY_ID=H.HIGHWAY_ID
                ORDER BY HU.UPDATE_ID DESC
            """)
            fill(tree, rows)

        def add():
            h_raw = gv(w["Highway"]).split(":")[0]
            sur   = gv(w["Surcharge (Rs)"])
            if not h_raw.isdigit():
                return notify("Validation", "Select a highway", "error")
            ok = db_exec(
                "INSERT INTO HIGHWAY_UPDATE(UPDATE_ID,HIGHWAY_ID,SURCHARGE,UPDATE_DATE)"
                " VALUES(HWU_SEQ.NEXTVAL,:1,:2,SYSDATE)",
                (int(h_raw), float(sur or 0)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Highway update recorded", "info")

        btn(f, "Add Update", add, C_GREEN, 130, "🔄").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 14. TOLL PLAZAS ─────────────────────────────────────────
    def _plazas(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("⛽  TOLL PLAZA MANAGEMENT", "Add and manage toll plazas")

        hways = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT HIGHWAY_ID,HIGHWAY_NAME FROM HIGHWAY ORDER BY HIGHWAY_ID")]
        svcs  = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT SERVICE_ID,SERVICE_NAME FROM SERVICE ORDER BY SERVICE_ID")]
        sec(p, "Add Toll Plaza", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        provs = ["Punjab","Sindh","KPK","Balochistan","ICT","AJK","GB"]
        fields = [
            ("Highway",    "Select",    lambda x: cmb(x, hways or ["—"])),
            ("Service",    "Select",    lambda x: cmb(x, svcs  or ["—"])),
            ("Plaza Name", "e.g. Kala Shah Kaku"),
            ("Location",   "e.g. KSK, Lahore"),
            ("Province",   "Select",   lambda x: cmb(x, provs)),
            ("Mile No",    "e.g. 25.5"),
            ("Exit No",    "e.g. E-5"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Plaza List", r + 1); r += 2
        tw, tree = mktable(
            p, ["PlazaID","Name","Highway","Province","Location","MileNo","ExitNo"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT TP.PLAZA_ID,TP.PLAZA_NAME,H.HIGHWAY_NAME,
                       NVL(TP.PROVINCE,'—'),NVL(TP.LOCATION,'—'),
                       NVL(TO_CHAR(TP.MILE_NO),'—'),NVL(TP.EXIT_NO,'—')
                FROM TOLL_PLAZA TP JOIN HIGHWAY H ON TP.HIGHWAY_ID=H.HIGHWAY_ID
                ORDER BY TP.PLAZA_ID
            """)
            fill(tree, rows)

        def add():
            h_raw = gv(w["Highway"]).split(":")[0]
            s_raw = gv(w["Service"]).split(":")[0]
            name  = gv(w["Plaza Name"])
            if not h_raw.isdigit() or not name:
                return notify("Validation", "Highway and name required", "error")
            ok = db_exec("""
                INSERT INTO TOLL_PLAZA(PLAZA_ID,HIGHWAY_ID,SERVICE_ID,PLAZA_NAME,
                    LOCATION,PROVINCE,MILE_NO,EXIT_NO)
                VALUES(PLAZA_SEQ.NEXTVAL,:1,:2,:3,:4,:5,:6,:7)
            """, (int(h_raw),
                  int(s_raw) if s_raw.isdigit() else None,
                  name, gv(w["Location"]), gv(w["Province"]),
                  float(gv(w["Mile No"]) or 0), gv(w["Exit No"])),
                commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Plaza added", "info")

        btn(f, "Add Plaza", add, C_GREEN, 130, "⛽").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 15. TERMINALS ───────────────────────────────────────────
    def _terminals(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🚧  TERMINAL MANAGEMENT", "IN/OUT terminals at toll plazas")

        plazas = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT PLAZA_ID,PLAZA_NAME FROM TOLL_PLAZA ORDER BY PLAZA_ID")]
        sec(p, "Add Terminal", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Plaza",         "Select", lambda x: cmb(x, plazas or ["—"])),
            ("Terminal Name", "e.g. KSK Entry 1"),
            ("Type",          "Select", lambda x: cmb(x, ["IN","OUT"])),
            ("Mile No",       "e.g. 25.5"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Terminal List", r + 1); r += 2
        tw, tree = mktable(
            p, ["TerminalID","Plaza","Name","Type","MileNo","Status"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT T.TERMINAL_ID, TP.PLAZA_NAME, T.TERMINAL_NAME,
                       T.TERMINAL_TYPE, NVL(TO_CHAR(T.MILE_NO),'—'), T.STATUS
                FROM TERMINAL T JOIN TOLL_PLAZA TP ON T.PLAZA_ID=TP.PLAZA_ID
                ORDER BY T.TERMINAL_ID
            """)
            fill(tree, rows)

        def add():
            p_raw = gv(w["Plaza"]).split(":")[0]
            name  = gv(w["Terminal Name"])
            ttype = gv(w["Type"])
            if not p_raw.isdigit() or not name:
                return notify("Validation", "Plaza and name required", "error")
            ok = db_exec(
                "INSERT INTO TERMINAL(TERMINAL_ID,PLAZA_ID,TERMINAL_NAME,TERMINAL_TYPE,MILE_NO,STATUS)"
                " VALUES(TERMINAL_SEQ.NEXTVAL,:1,:2,:3,:4,'ACTIVE')",
                (int(p_raw), name, ttype,
                 float(gv(w["Mile No"]) or 0)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Terminal added", "info")

        btn(f, "Add Terminal", add, C_GREEN, 140, "🚧").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 16. SERVICES ────────────────────────────────────────────
    def _services(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🛎  SERVICE MANAGEMENT", "Toll service types and rates")

        sec(p, "Add Service", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Service Name",   "e.g. Standard Toll"),
            ("Service Type",   "e.g. TOLL"),
            ("Rate Per Km",    "e.g. 5.00"),
            ("Base Rate",      "e.g. 4.50"),
            ("Surcharge Rate", "e.g. 0"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Service List", r + 1); r += 2
        tw, tree = mktable(
            p, ["ServiceID","Name","Type","Rate/Km","BaseRate","Surcharge","EffectiveFrom"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT SERVICE_ID, SERVICE_NAME, NVL(SERVICE_TYPE,'—'),
                       NVL(TO_CHAR(TOLL_RATE_PER_KM),'—'),
                       NVL(TO_CHAR(BASE_RATE_PER_KM),'—'),
                       NVL(TO_CHAR(SURCHARGE_RATE),'0'),
                       TO_CHAR(EFFECTIVE_FROM,'DD-Mon-YY')
                FROM SERVICE ORDER BY SERVICE_ID
            """)
            fill(tree, rows)

        def add():
            name = gv(w["Service Name"])
            if not name:
                return notify("Validation", "Name required", "error")
            ok = db_exec("""
                INSERT INTO SERVICE(SERVICE_ID,SERVICE_NAME,SERVICE_TYPE,
                    TOLL_RATE_PER_KM,BASE_RATE_PER_KM,SURCHARGE_RATE,EFFECTIVE_FROM)
                VALUES(SVC_SEQ.NEXTVAL,:1,:2,:3,:4,:5,SYSDATE)
            """, (name, gv(w["Service Type"]),
                  float(gv(w["Rate Per Km"]) or 0),
                  float(gv(w["Base Rate"]) or 0),
                  float(gv(w["Surcharge Rate"]) or 0)), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Service added", "info")

        btn(f, "Add Service", add, C_GREEN, 130, "🛎").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 17. ALL TRANSACTIONS ────────────────────────────────────
    def _txns(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💸  ALL TRANSACTIONS", "Full transaction ledger — admin view")

        sec(p, "Full Transaction Log", r); r += 1
        tw, tree = mktable(
            p, ["TxnID","TagID","Plate","Plaza","EntryTerm","ExitTerm",
                "Dist(Km)","Rate","Base","Surcharge","Discount","Total(Rs)","Date"], 12)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1

        def refresh():
            rows = db_fetch("""
                SELECT TH.TRANSACTION_ID, TH.TAG_ID, V.PLATE_NUMBER,
                       NVL(TP.PLAZA_NAME,'—'), NVL(TE.TERMINAL_NAME,'—'),
                       NVL(TX.TERMINAL_NAME,'—'),
                       TH.DISTANCE_TRAVELLED, TH.TOLL_RATE_PER_KM,
                       TH.BASE_TOLL, TH.SURCHARGE, TH.EXEMPTION_DISCOUNT,
                       TH.TOTAL_AMOUNT,
                       TO_CHAR(TH.TRANSACTION_DATE,'DD-Mon-YY HH24:MI')
                FROM TRANSACTION_HISTORY TH
                LEFT JOIN TAG T ON TH.TAG_ID = T.TAG_ID
                LEFT JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                LEFT JOIN TOLL_PLAZA TP ON TH.PLAZA_ID = TP.PLAZA_ID
                LEFT JOIN TERMINAL TE ON TH.ENTRY_TERMINAL_ID = TE.TERMINAL_ID
                LEFT JOIN TERMINAL TX ON TH.EXIT_TERMINAL_ID = TX.TERMINAL_ID
                ORDER BY TH.TRANSACTION_ID DESC
            """)
            fill(tree, rows)

        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 18. EMPLOYEES ───────────────────────────────────────────
    def _employees(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("👷  EMPLOYEE MANAGEMENT", "Toll plaza staff")

        plazas = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT PLAZA_ID,PLAZA_NAME FROM TOLL_PLAZA ORDER BY PLAZA_ID")]
        sec(p, "Add Employee", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        desig = ["Toll Collector","Supervisor","Manager","Security Guard","IT Staff","Mechanic"]
        fields = [
            ("Name",        "Full Name"),
            ("Phone",       "03XX-XXXXXXX"),
            ("Designation", "Select", lambda x: cmb(x, desig)),
            ("Plaza",       "Select", lambda x: cmb(x, plazas or ["—"])),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Employee List", r + 1); r += 2
        tw, tree = mktable(p, ["EmpID","Name","Phone","Designation","Plaza"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT E.EMPLOYEE_ID, E.EMPLOYEE_NAME, E.PHONE,
                       NVL(E.DESIGNATION,'—'), NVL(TP.PLAZA_NAME,'—')
                FROM EMPLOYEE E
                LEFT JOIN TOLL_PLAZA TP ON E.PLAZA_ID = TP.PLAZA_ID
                ORDER BY E.EMPLOYEE_ID DESC
            """)
            fill(tree, rows)

        def add():
            name = gv(w["Name"])
            if not name:
                return notify("Validation", "Name required", "error")
            p_raw = gv(w["Plaza"]).split(":")[0]
            ok = db_exec(
                "INSERT INTO EMPLOYEE(EMPLOYEE_ID,EMPLOYEE_NAME,PHONE,DESIGNATION,PLAZA_ID)"
                " VALUES(EMP_SEQ.NEXTVAL,:1,:2,:3,:4)",
                (name, gv(w["Phone"]), gv(w["Designation"]),
                 int(p_raw) if p_raw.isdigit() else None), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Employee added", "info")

        btn(f, "Add Employee", add, C_GREEN, 140, "👷").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 19. CAMERAS ─────────────────────────────────────────────
    def _cameras(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("📷  CAMERA SYSTEM", "Surveillance cameras at plazas")

        plazas = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT PLAZA_ID,PLAZA_NAME FROM TOLL_PLAZA ORDER BY PLAZA_ID")]
        sec(p, "Add Camera", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        fields = [
            ("Plaza",    "Select",   lambda x: cmb(x, plazas or ["—"])),
            ("Location", "e.g. Entry Gate Left"),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Camera List", r + 1); r += 2
        tw, tree = mktable(p, ["CameraID","Plaza","Location","Status"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT C.CAMERA_ID, TP.PLAZA_NAME, NVL(C.CAMERA_LOCATION,'—'), C.STATUS
                FROM CAMERA_SYSTEM C JOIN TOLL_PLAZA TP ON C.PLAZA_ID=TP.PLAZA_ID
                ORDER BY C.CAMERA_ID DESC
            """)
            fill(tree, rows)

        def add():
            p_raw = gv(w["Plaza"]).split(":")[0]
            if not p_raw.isdigit():
                return notify("Validation", "Select a plaza", "error")
            ok = db_exec(
                "INSERT INTO CAMERA_SYSTEM(CAMERA_ID,PLAZA_ID,CAMERA_LOCATION,STATUS)"
                " VALUES(CAM_SEQ.NEXTVAL,:1,:2,'ACTIVE')",
                (int(p_raw), gv(w["Location"])), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Camera added", "info")

        def toggle():
            sel = tree.selection()
            if not sel: return notify("Select","Select a camera","warning")
            cid = tree.item(sel[0])["values"][0]
            cur = tree.item(sel[0])["values"][3]
            new = "INACTIVE" if cur == "ACTIVE" else "ACTIVE"
            db_exec("UPDATE CAMERA_SYSTEM SET STATUS=:1 WHERE CAMERA_ID=:2", (new, cid), commit=True)
            refresh()

        btn(f, "Add Camera", add, C_GREEN, 130, "📷").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=2, padx=14, pady=6, sticky="e")
        btn(p, "Toggle Status", toggle, C_YELLOW, 130).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 20. LANES ───────────────────────────────────────────────
    def _lanes(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🚦  LANE MANAGEMENT", "Traffic lanes at plazas")

        plazas = [f"{x[0]}:{x[1]}" for x in db_fetch("SELECT PLAZA_ID,PLAZA_NAME FROM TOLL_PLAZA ORDER BY PLAZA_ID")]
        sec(p, "Add Lane", r); r += 1
        f = frm(p)
        f.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ltypes = ["M-Tag","Cash","Mixed","Heavy Vehicle","Motorcycle"]
        fields = [
            ("Plaza",     "Select", lambda x: cmb(x, plazas or ["—"])),
            ("Lane Type", "Select", lambda x: cmb(x, ltypes)),
        ]
        w, nr = bform(f, fields, 0, 4)

        sec(p, "Lane List", r + 1); r += 2
        tw, tree = mktable(p, ["LaneID","Plaza","Type","Status"], 8)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")

        def refresh():
            rows = db_fetch("""
                SELECT L.LANE_ID, TP.PLAZA_NAME, NVL(L.LANE_TYPE,'—'), L.STATUS
                FROM LANE L JOIN TOLL_PLAZA TP ON L.PLAZA_ID=TP.PLAZA_ID
                ORDER BY L.LANE_ID DESC
            """)
            fill(tree, rows)

        def add():
            p_raw = gv(w["Plaza"]).split(":")[0]
            if not p_raw.isdigit():
                return notify("Validation", "Select a plaza", "error")
            ok = db_exec(
                "INSERT INTO LANE(LANE_ID,PLAZA_ID,LANE_TYPE,STATUS)"
                " VALUES(LANE_SEQ.NEXTVAL,:1,:2,'OPEN')",
                (int(p_raw), gv(w["Lane Type"])), commit=True)
            if ok:
                refresh(); clr(w)
                notify("Success", "Lane added", "info")

        def toggle():
            sel = tree.selection()
            if not sel: return notify("Select","Select a lane","warning")
            lid = tree.item(sel[0])["values"][0]
            cur = tree.item(sel[0])["values"][3]
            new = "CLOSED" if cur == "OPEN" else "OPEN"
            db_exec("UPDATE LANE SET STATUS=:1 WHERE LANE_ID=:2", (new, lid), commit=True)
            refresh()

        btn(f, "Add Lane", add, C_GREEN, 120, "🚦").grid(row=nr, column=0, padx=8, pady=10)
        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r+1, column=2, padx=14, pady=6, sticky="e")
        btn(p, "Open/Close Lane", toggle, C_YELLOW, 140).grid(row=r+1, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 21. ALERTS ──────────────────────────────────────────────
    def _alerts(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("🔔  ALERT NOTIFICATIONS", "System-generated alerts for all tags")

        sec(p, "All Alerts", r); r += 1
        tw, tree = mktable(
            p, ["AlertID","TagID","Owner","Plate","Message","Date"], 12)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1

        def refresh():
            rows = db_fetch("""
                SELECT AN.ALERT_ID, AN.TAG_ID, U.NAME, V.PLATE_NUMBER,
                       AN.ALERT_MESSAGE, TO_CHAR(AN.ALERT_DATE,'DD-Mon-YY HH24:MI')
                FROM ALERT_NOTIFICATION AN
                JOIN TAG T ON AN.TAG_ID = T.TAG_ID
                JOIN USERS U ON T.USER_ID = U.USER_ID
                JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
                ORDER BY AN.ALERT_ID DESC
            """)
            fill(tree, rows)

        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 22. ALL FEEDBACK ────────────────────────────────────────
    def _feedback(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("💬  USER FEEDBACK", "All user feedback and ratings")

        sec(p, "Feedback Log", r); r += 1
        tw, tree = mktable(p, ["FeedbackID","UserID","Name","Rating","Comments"], 12)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1

        def refresh():
            rows = db_fetch("""
                SELECT F.FEEDBACK_ID, F.USER_ID, U.NAME, F.RATING, NVL(F.COMMENTS,'—')
                FROM FEEDBACK F JOIN USERS U ON F.USER_ID = U.USER_ID
                ORDER BY F.FEEDBACK_ID DESC
            """)
            fill(tree, rows)

        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 23. ADMIN LOG ───────────────────────────────────────────
    def _adminlog(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("📋  ADMIN AUDIT LOG", "All admin actions — tamper-evident trail")

        sec(p, "Admin Action Log", r); r += 1
        tw, tree = mktable(
            p, ["LogID","AdminID","AdminName","ActionType","Detail","Timestamp"], 14)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1

        def refresh():
            rows = db_fetch("""
                SELECT L.LOG_ID, L.ADMIN_USER_ID, NVL(U.NAME,'System'),
                       L.ACTION_TYPE, NVL(L.ACTION_DETAIL,'—'),
                       TO_CHAR(L.LOG_DATE,'DD-Mon-YY HH24:MI:SS')
                FROM ADMIN_LOG L
                LEFT JOIN USERS U ON L.ADMIN_USER_ID = U.USER_ID
                ORDER BY L.LOG_ID DESC
            """)
            fill(tree, rows)

        btn(p, "↻ Refresh", refresh, C_ACCENT, 110).grid(row=r, column=3, padx=14, pady=6, sticky="e")
        refresh()

    # ── 24. REPORTS ─────────────────────────────────────────────
    def _reports(self):
        p = self.pane
        p.grid_columnconfigure((0, 1, 2, 3), weight=1)
        r = self._title("📈  REPORTS & ANALYTICS", "Live analytics — Oracle DB queries")

        def q(sql, fb=0):
            row = db_fetchone(sql)
            return row[0] if row and row[0] is not None else fb

        kpis = [
            ("Total Revenue",   f"Rs {q('SELECT NVL(SUM(TOTAL_AMOUNT),0) FROM TRANSACTION_HISTORY'):,.0f}", C_GREEN),
            ("Transactions",    str(q("SELECT COUNT(*) FROM TRANSACTION_HISTORY")),            C_ACCENT),
            ("Avg Toll",        f"Rs {q('SELECT NVL(AVG(TOTAL_AMOUNT),0) FROM TRANSACTION_HISTORY'):,.0f}", C_ACT2),
            ("Total Distance",  f"{q('SELECT NVL(SUM(DISTANCE_TRAVELLED),0) FROM TRANSACTION_HISTORY'):.0f} Km", "#7C3AED"),
            ("Low Bal Tags",    str(q("SELECT COUNT(*) FROM TAG WHERE BALANCE<500")),           C_RED),
            ("Active Tags",     str(q("SELECT COUNT(*) FROM TAG WHERE STATUS='ACTIVE'")),       C_GREEN),
        ]
        sec(p, "Summary KPIs", r); r += 1
        kf = frm(p)
        kf.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        kf.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        for i, (label, val, col) in enumerate(kpis):
            cf = ctk.CTkFrame(kf, fg_color="#F0F9FF", corner_radius=10,
                              border_width=2, border_color=col)
            cf.grid(row=0, column=i, padx=8, pady=12, sticky="ew")
            ctk.CTkLabel(cf, text=val,
                         font=("Segoe UI", 15, "bold"),
                         text_color=col).pack(pady=(12, 2))
            ctk.CTkLabel(cf, text=label,
                         font=("Segoe UI", 8, "bold"),
                         text_color=C_MUTED).pack(pady=(0, 12), padx=6)
        r += 1

        sec(p, "Transaction Report — Distance × Rate Formula", r); r += 1
        tw, tree = mktable(
            p, ["TxnID","TagID","Plate","Plaza","EntryTerm","ExitTerm",
                "Dist(Km)","Rate/Km","BaseToll","Surcharge","Discount","Total(Rs)","Date"], 10)
        tw.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1
        rows = db_fetch("""
            SELECT TH.TRANSACTION_ID, TH.TAG_ID, V.PLATE_NUMBER,
                   TP.PLAZA_NAME, TE.TERMINAL_NAME, TX.TERMINAL_NAME,
                   TH.DISTANCE_TRAVELLED, TH.TOLL_RATE_PER_KM,
                   TH.BASE_TOLL, TH.SURCHARGE, TH.EXEMPTION_DISCOUNT,
                   TH.TOTAL_AMOUNT,
                   TO_CHAR(TH.TRANSACTION_DATE,'DD-Mon-YY HH24:MI')
            FROM TRANSACTION_HISTORY TH
            LEFT JOIN TAG T ON TH.TAG_ID = T.TAG_ID
            LEFT JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            LEFT JOIN TOLL_PLAZA TP ON TH.PLAZA_ID = TP.PLAZA_ID
            LEFT JOIN TERMINAL TE ON TH.ENTRY_TERMINAL_ID = TE.TERMINAL_ID
            LEFT JOIN TERMINAL TX ON TH.EXIT_TERMINAL_ID = TX.TERMINAL_ID
            ORDER BY TH.TRANSACTION_ID DESC
        """)
        fill(tree, rows)

        sec(p, "Revenue by Plaza — GROUP BY", r); r += 1
        tw3, tree3 = mktable(p, ["PlazaName","Transactions","Total Revenue (Rs)","Avg Toll (Rs)"], 6)
        tw3.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1
        rows3 = db_fetch("""
            SELECT TP.PLAZA_NAME, COUNT(*),
                   NVL(SUM(TH.TOTAL_AMOUNT),0),
                   ROUND(NVL(AVG(TH.TOTAL_AMOUNT),0),2)
            FROM TRANSACTION_HISTORY TH
            JOIN TOLL_PLAZA TP ON TH.PLAZA_ID = TP.PLAZA_ID
            GROUP BY TP.PLAZA_NAME ORDER BY 3 DESC
        """)
        fill(tree3, rows3)

        sec(p, "Tag Balance Report — LOW BALANCE WARNING", r); r += 1
        tw2, tree2 = mktable(
            p, ["TagID","Owner","Plate","VehicleType","Balance","ReserveBalance","Status"], 8)
        tw2.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        r += 1
        rows2 = db_fetch("""
            SELECT T.TAG_ID, U.NAME, V.PLATE_NUMBER, VT.VEHICLE_CLASS,
                   T.BALANCE, T.RESERVE_BALANCE, T.STATUS
            FROM TAG T
            JOIN USERS U ON T.USER_ID = U.USER_ID
            LEFT JOIN VEHICLE V ON T.VEHICLE_ID = V.VEHICLE_ID
            LEFT JOIN VEHICLE_TYPE VT ON V.TYPE_ID = VT.TYPE_ID
            ORDER BY T.BALANCE ASC
        """)
        fill(tree2, rows2)

        sec(p, "User Roles — JOIN Example", r); r += 1
        tw5, tree5 = mktable(p, ["Name","Username","Role","AssignedDate"], 5)
        tw5.grid(row=r, column=0, columnspan=4, padx=14, pady=6, sticky="ew")
        rows5 = db_fetch("""
            SELECT U.NAME, U.USERNAME, R.ROLE_NAME,
                   TO_CHAR(UR.ASSIGNED_DATE,'YYYY-MM-DD')
            FROM USERS U
            JOIN USER_ROLE UR ON U.USER_ID = UR.USER_ID
            JOIN ROLE R ON UR.ROLE_ID = R.ROLE_ID
        """)
        fill(tree5, rows5)


# ══════════════════════════════════════════════════════════════════
#  REQUIRED SEQUENCES IN ORACLE (run once if not done)
# ══════════════════════════════════════════════════════════════════
# CREATE SEQUENCE USER_SEQ        START WITH 4    INCREMENT BY 1;
# CREATE SEQUENCE VEHICLE_SEQ     START WITH 104  INCREMENT BY 1;
# CREATE SEQUENCE TAG_SEQ         START WITH 1004 INCREMENT BY 1;
# CREATE SEQUENCE TRANSACTION_SEQ START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE RECHARGE_SEQ    START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE PAYMENT_SEQ     START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE EMP_SEQ         START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE ALERT_SEQ       START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE FEEDBACK_SEQ    START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE HWY_SEQ         START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE HWU_SEQ         START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE PLAZA_SEQ       START WITH 4    INCREMENT BY 1;
# CREATE SEQUENCE SVC_SEQ         START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE CAM_SEQ         START WITH 4    INCREMENT BY 1;
# CREATE SEQUENCE MOTORWAY_SEQ    START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE TERMINAL_SEQ    START WITH 5    INCREMENT BY 1;
# CREATE SEQUENCE EXEMPTION_SEQ   START WITH 2    INCREMENT BY 1;
# CREATE SEQUENCE ADMIN_LOG_SEQ   START WITH 1    INCREMENT BY 1;
# CREATE SEQUENCE USER_ROLE_SEQ   START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE LANE_SEQ        START WITH 3    INCREMENT BY 1;
# CREATE SEQUENCE VTYPE_SEQ       START WITH 8    INCREMENT BY 1;

# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        import customtkinter
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    try:
        import oracledb
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "oracledb"])

    if not DB_OK:
        print(f"\n⚠  Oracle connection failed: {DB_ERR}")
        print("  → Edit DB_CONFIG at top of file")
        print("  → App launches in demo mode; tables show empty until connected\n")

    app = LoginScreen()
    app.mainloop()