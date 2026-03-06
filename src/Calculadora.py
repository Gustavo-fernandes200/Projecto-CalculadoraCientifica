"""
/////////////////////////////////////////////////////////////////////////////////////////
  TRABALHO PRÁTICO 1 — Calculadora Científica
  Linguagem: Python | Framework UI: Flet
  Baseado no tutorial: https://docs.flet.dev/tutorials/calculator/ + Pesquisa Cientifica
////////////////////////////////////////////////////////////////////////////////////////

*********************************************************************************
* UAlg | ISE
* TP1 – Calculadora Científica
-------------------------------------------------------------------------------
Funcionalidades:

-------------------------------------------------------------------------------
* AUTORES:
            Gustavo Fernandes
* DATA: 22/02/2026
*********************************************************************************
"""

# ===============================================================================
#                                     Bibiloteca
# ===============================================================================

import flet as ft
import duckdb as db
import sympy as sp
from sympy import (
    sqrt, log, sin, cos, tan, asin, acos, atan, pi, E, factorial,
    Abs, ceiling, floor
)
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import math
import re
import os
import sys
import json
from functools import lru_cache
from typing import Tuple, Union, Dict, Any
from pathlib import Path

# ===============================================================================
#                                     Configuração
# ===============================================================================

@dataclass(frozen = True)
class AppConfig:
  title        : str              = "Calculadora Cientifica"
  max_history  : Union[int,float] = float('inf')  # infinito
  modes        : Tuple[str, ...]  = ("Padrão", "Científica")
  default_mode : str              = "Padrão"
  live_preview : bool             = False

  def validated(self) -> "AppConfig":
      mh_raw = self.max_history

      if isinstance(mh_raw, (int, float)) and math.isfinite(mh_raw):
          mh = int(mh_raw)
          if mh < 1:
              mh = 1
      else:
          mh = float("inf")

      dm = self.default_mode if self.default_mode in self.modes else "Padrão"

      return AppConfig(
          title=self.title,
          max_history=mh,
          modes=self.modes,
          default_mode=dm,
          live_preview=bool(self.live_preview),
      )

CFG = AppConfig().validated()

# ===============================================================================
#                               Configuração de Cores 
# ===============================================================================

C = {
    # ── Fundos ────────────────────────────────────────────

    "bg"          : "#0D1B3E",   # tema: navy profundo (Google Calc Android)
    "surface"     : "#0F2045",
    "surface2"    : "#142650",
    "card"        : "#102040",
    "card2"       : "#162A55",
    "border"      : "#1A2E58",
    "border_light": "#22406A",

    # ── Botões ────────────────────────────────────────────

    "btn_digit"   : "#1D3A70",   # azul médio — dígitos
    "btn_op"      : "#2B5CC8",   # azul brilhante — operadores
    "btn_fn"      : "#1D3A70",   # igual dígitos — funções científicas
    "btn_util"    : "#3D72E8",   # azul claro — AC / () / %
    "btn_extra"   : "#1D3A70",
    "btn_prog"    : "#142050",
    "btn_clear"   : "#1D3A70",
    "btn_eq"      : "#BF50C8",   # rosa/magenta — botão =

    # ── Acents (mantidos para modos não-padrão) ───────────

    "btn_ac"      : "#3D72E8",
    "accent"      : "#BF50C8",
    "accent_dim"  : "#BF50C815",
    "accent2"     : "#3D72E8",
    "accent2_dim" : "#3D72E815",
    "accent3"     : "#5BA8FF",
    "accent3_dim" : "#5BA8FF15",
    "accent4"     : "#FBBF24",
    "accent4_dim" : "#FBBF2415",
    "accent5"     : "#F472B6",
    "accent5_dim" : "#F472B615",
    "danger"      : "#F87171",
    "danger_dim"  : "#F8717118",

    # ── Texto ─────────────────────────────────────────────
    "text_primary": "#FFFFFF",
    "text_second" : "#5C7EA8",
    "text_hint"   : "#2E4870",
    "text_fn"     : "#7BBCFF",
    "text_op"     : "#FFFFFF",
    "text_eq"     : "#FFFFFF",
}

MODE_COLORS = {

    "Padrão":      C["accent"],
    "Científica":  C["accent2"],
}

MODE_ICONS = {

    "Padrão":      ft.Icons.CALCULATE_ROUNDED,
    "Científica":  ft.Icons.FUNCTIONS_ROUNDED,
}

BTN_SIMBOLS = {

    # ── Dígitos ────────────────────────────────────────────────────────────────
    "0"    : {"bg": C["btn_digit"],                              "fs": 22},
    "1"    : {"bg": C["btn_digit"],                              "fs": 22},
    "2"    : {"bg": C["btn_digit"],                              "fs": 22},
    "3"    : {"bg": C["btn_digit"],                              "fs": 22},
    "4"    : {"bg": C["btn_digit"],                              "fs": 22},
    "5"    : {"bg": C["btn_digit"],                              "fs": 22},
    "6"    : {"bg": C["btn_digit"],                              "fs": 22},
    "7"    : {"bg": C["btn_digit"],                              "fs": 22},
    "8"    : {"bg": C["btn_digit"],                              "fs": 22},
    "9"    : {"bg": C["btn_digit"],                              "fs": 22},
    "."    : {"bg": C["btn_digit"],                              "fs": 26,
              "fw": ft.FontWeight.W_700},

    # ── Operadores aritméticos ─────────────────────────────────────────────────
    "÷"    : {"bg": C["btn_op"],                                 "fs": 22},
    "×"    : {"bg": C["btn_op"],                                 "fs": 22},
    "−"    : {"bg": C["btn_op"],                                 "fs": 22},
    "+"    : {"bg": C["btn_op"],                                 "fs": 22},

    # ── Utilitários (AC / parênteses / percentagem / retrocesso) ──────────────
    "AC"   : {"bg": C["btn_util"],  "fs": 17, "fw": ft.FontWeight.W_700, "glow": C["btn_util"] + "35"},
    "( )"  : {"bg": C["btn_util"],  "fs": 15},
    "%"    : {"bg": C["btn_util"],  "fs": 18},
    "⌫"   : {"bg": C["btn_digit"], "fs": 20},

    # ── Funções científicas -  Trigonométricas básicas ────────────────────────────────────────────────────
    
    "sin"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "cos"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "tan"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},

    # ── Trigonométricas inversas ──────────────────────────────────────────────────────────────────────────────

    "asin" : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    "acos" : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    "atan" : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},

    # Constante π (cor especial dourada)

    "π"    : {"bg": C["btn_fn"], "fg": C["accent4"], "bc": C["accent4"] + "40", "fs": 14},

    # Inversão e potências

    "1/x"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "√"    : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 15},
    "xⁿ"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "x²"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},

    # Logaritmos e exponencial

    "log"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "ln"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "eˣ"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},

    # Fatorial e módulo

    "n!"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "|x|"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 12},

    # Arredondamento e parênteses individuais

    "ceil" : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    "floor": {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    "("    : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 16},
    ")"    : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 16},
}

def mk(key: str, handler, *, h=None, bg=None, fg=None) -> ft.Container:
    
    cfg   = BTN_SIMBOLS[key]
    label = key

    return btn(
        label, handler,
        bg   = bg   or cfg["bg"],
        fg   = fg   or cfg.get("fg", "#FFFFFF"),
        bc   = cfg.get("bc"),
        fs   = cfg["fs"],
        fw   = cfg.get("fw", ft.FontWeight.W_400),
        glow = cfg.get("glow"),
        h    = h,
    )

UI = {
  "page_bg"      : C["bg"],
  "display_bg"   : C["bg"],
  "display_main" : C["text_primary"],
  "display_expr" : C["text_second"],
  "key_bg"       : C["surface2"],
  "key_text"     : C["text_primary"],
  "mem_text"     : C["text_second"],
  "op_text"      : C["accent3"],
  "eq_bg"        : C["accent3"],
  "eq_text"      : "#FFFFFF",
  "top_btn_bg"   : C["surface2"],
  "top_btn_icon" : C["text_primary"],
  "shadow"       : "#00000090",
}

# ── Constantes de estilo dos botões ─────────────────────────────────────────────

BTN_H      = 58   # altura botão portrait (expand dinâmico)
BTN_H_LAND = 50   # altura botão landscape (fixa — permite overflow + scroll)
BTN_H_FN   = 46   # funções científicas
BTN_R      = 14   # border-radius

# ===============================================================================
#                               Motor de Cálculo
# ===============================================================================

# ── Namespace SymPy  ─────────────────────────────────────────────────

_NS = {
    "sqrt":sqrt, "log":log, "ln":log,
    "sin":sin, "cos":cos, "tan":tan,
    "asin":asin, "acos":acos, "atan":atan,
    "Abs":Abs, "ceiling":ceiling, "floor":floor,
    "pi":pi, "E":E, "factorial":factorial, "exp":sp.exp,
}

# ── Namespace Python/math (Tier 1 — fast path) ───────────────────────────────

_FAST_NS: dict = {
    "__builtins__": {},
    # Funções trigonométricas
    "sin":   math.sin,   "cos":   math.cos,   "tan":   math.tan,
    "asin":  math.asin,  "acos":  math.acos,  "atan":  math.atan,
    # Funções matemáticas
    "sqrt":  math.sqrt,  "log":   math.log,   "log10": math.log10,
    "exp":   math.exp,   "abs":   abs,
    "ceil":  math.ceil,  "floor": math.floor,
    "factorial": math.factorial,
    # Constantes
    "pi":    math.pi,    "e":     math.e,     "E":     math.e,
}

# ── Regexes pré-compilados ────────────────────────────────────────────────────

_RE_FACTORIAL = re.compile(r"(\d+)!")
_RE_SUBS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bsqrt\b"),  "sqrt"),
    (re.compile(r"\bln\b"),    "log"),
    (re.compile(r"\blog\b"),   "log"),
    (re.compile(r"\bsin\b"),   "sin"),
    (re.compile(r"\bcos\b"),   "cos"),
    (re.compile(r"\btan\b"),   "tan"),
    (re.compile(r"\basin\b"),  "asin"),
    (re.compile(r"\bacos\b"),  "acos"),
    (re.compile(r"\batan\b"),  "atan"),
    (re.compile(r"\babs\b"),   "Abs"),
    (re.compile(r"\bceil\b"),  "ceiling"),
    (re.compile(r"\bfloor\b"), "floor"),
    (re.compile(r"\bexp\b"),   "exp"),
    (re.compile(r"π"),         "pi"),
    (re.compile(r"×"),         "*"),
    (re.compile(r"÷"),         "/"),
    (re.compile(r"\^"),        "**"),
]

# ── Tier 1: fast path ────────────────────────────────────────────────────────
@lru_cache(maxsize=4096)
def _eval_fast(expr: str) -> str:

    # "Abs(" → "abs(" para compatibilidade com _FAST_NS
    e = expr.replace("Abs(", "abs(").replace("ceiling(", "ceil(")
    v = eval(e, _FAST_NS)
    if not isinstance(v, (int, float, complex)):
        raise TypeError("Resultado não numérico")
    f = float(v)
    if not math.isfinite(f):
        raise ValueError("Resultado indefinido.")
    return _fmt(int(f) if f == int(f) else f)

# ── Tier 2: SymPy (fallback simbólico) ───────────────────────────────────────
@lru_cache(maxsize=512)
def _eval_sympy(expr: str) -> str:

    sym = sp.sympify(expr, locals=_NS)
    sym = sp.simplify(sym)
    if sym.is_number:
        f = float(sym)
        if not math.isfinite(f):
            raise ValueError("Resultado indefinido.")
        v = int(f) if sym == int(f) else f
        return _fmt(v)
    return str(sym)

def _fmt(v) -> str:
    if isinstance(v, int):
        return f"{v:,}".replace(",", "\u2009")
    return f"{v:,.10f}".rstrip("0").rstrip(".").replace(",", "\u2009")

def _fmt_expr(expr: str) -> str:

    def _sep(m):
        s = m.group(0)
        if len(s) < 4:
            return s
        buf = []
        for i, ch in enumerate(reversed(s)):
            if i > 0 and i % 3 == 0:
                buf.append("\u2009")
            buf.append(ch)
        return "".join(reversed(buf))
    return re.sub(r"\d+", _sep, expr)

def calcular(expression: str) -> str:

    # ── Normalização com regexes pré-compilados ───────────────────────────────
    e = expression.strip()
    for pattern, repl in _RE_SUBS:
        e = pattern.sub(repl, e)
    e = _RE_FACTORIAL.sub(lambda m: f"factorial({m.group(1)})", e)

    # ── Tier 1 — Fast path ────────────────────────────────────────────────────
    try:
        return _eval_fast(e)
    except Exception:
        pass  # não computável no fast path → tentar SymPy

    # ── Tier 2 — SymPy (fallback simbólico) ──────────────────────────────────
    try:
        return _eval_sympy(e)
    except Exception as ex:
        raise ValueError(str(ex))


def normalizar_expr(expr: str) -> str:
    """
    Converte notação matemática humana em Python válido.

    Casos tratados:
      1/2x-2        → 1/2*x-2        (multiplicação implícita número+variável)
      3sin(x)       → 3*sin(x)       (número + função)
      2(x+1)        → 2*(x+1)        (número + parêntese)
      (x+1)(x-1)   → (x+1)*(x-1)   (fecho + abertura)
      sin(x)cos(x)  → sin(x)*cos(x)  (fecho + função)
      2πx           → 2*pi*x         (π + variável)
      e^x           → e**x           (potência tipográfica)
      log10(x)      → log10(x)       (inalterado — dígito dentro de identificador)
      2log10(x)     → 2*log10(x)     (número antes de log10)
    """
    e = expr.strip()
    e = e.replace("^",  "**")
    e = e.replace("π",  "pi")
    e = e.replace("×",  "*")
    e = e.replace("÷",  "/")
    e = e.replace("−",  "-")

    # Número no início de token + letra/( → * (?<![a-zA-Z0-9]) garante que não apanha dígitos dentro de identificadores como "log10" (onde "0" é precedido de "1" que é precedido de "g")
    e = re.sub(r"(?<![a-zA-Z0-9])(\d+)([a-zA-Z(])", r"\1*\2", e)

    # "pi" + letra/( → * (?<![a-zA-Z]) garante que "pi" não é parte de um identificador maior como "pivot" ou "exp(pi*x)"
    e = re.sub(r"(?<![a-zA-Z])(pi)(?=[a-zA-Z(])", r"\1*", e)

    # "e" isolado (constante de Euler) + letra/( → * (?<![a-zA-Z]) garante que "e" é isolado e não parte de um identificador maior como "exp" ou "sec")
    e = re.sub(r"\b(e)\b(?=[a-zA-Z(])", r"\1*", e)

    # Fecho ) + letra/( → * (?<![a-zA-Z]) garante que não apanha letras dentro de identificadores como "sin(x)" ou "log10(x)"
    e = re.sub(r"\)([a-zA-Z(])", r")*\1", e)

    return e

# ================================ Historico ====================================
class HistDB:
    def __init__(self, db_path: str, max_history: Union[int, float] = 200):
        self.db_path = str(db_path)
        self.max_history = max_history

        # Garante que a pasta existe antes de criar o arquivo DB (evita erros de "pasta não encontrada")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Inicializa a tabela de histórico se ainda não existir 
        with db.connect(self.db_path) as c:
            c.execute("CREATE SEQUENCE IF NOT EXISTS hseq START 1")
            c.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY DEFAULT nextval('hseq'),
                    mode VARCHAR,
                    expression VARCHAR,
                    result VARCHAR,
                    ts TIMESTAMP DEFAULT current_timestamp
                )
            """)

    def insert(self, mode, expr, result):
        expr = (expr or "")[:256]
        result = (result or "")[:512]

        with db.connect(self.db_path) as c:
            c.execute("BEGIN")
            try:
                c.execute(
                    "INSERT INTO history(mode, expression, result) VALUES (?, ?, ?)",
                    [mode, expr, result],
                )
                self._trim_in_conn(c)
                c.execute("COMMIT")
            except Exception:
                c.execute("ROLLBACK")
                raise

    def _trim_in_conn(self, c):
        mh = self.max_history

        # Validações de segurança para max_history (pode ser configurado via client_storage → evitar SQL injection ou valores absurdos que travem a app)
        if mh is None:
            return
        if isinstance(mh, float) and math.isinf(mh):
            return

        # Garantir que mh é um inteiro positivo razoável
        mh = int(mh)
        if mh < 1:
            mh = 1

        # Verificar quantas entradas existem e deletar as mais antigas se excederem max_history
        n = c.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        if n > mh:
            c.execute("""
                DELETE FROM history
                WHERE id IN (
                    SELECT id
                    FROM history
                    ORDER BY ts ASC, id ASC
                    LIMIT ?
                )
            """, [n - mh])

    def fetch(self, mode=None):
        with db.connect(self.db_path) as c:
            if mode:
                rows = c.execute("""
                    SELECT id, mode, expression, result, ts
                    FROM history
                    WHERE mode = ?
                    ORDER BY ts DESC, id DESC
                """, [mode]).fetchall()
            else:
                rows = c.execute("""
                    SELECT id, mode, expression, result, ts
                    FROM history
                    ORDER BY ts DESC, id DESC
                """).fetchall()

        return [
            {
                "id": r[0],
                "mode": r[1],
                "expression": r[2],
                "result": r[3],
                "ts": str(r[4])[:16],
            }
            for r in rows
        ]

    def delete(self, eid):
        with db.connect(self.db_path) as c:
            c.execute("DELETE FROM history WHERE id = ?", [int(eid)])

    def clear(self, mode=None):
        with db.connect(self.db_path) as c:
            if mode:
                c.execute("DELETE FROM history WHERE mode = ?", [mode])
            else:
                c.execute("DELETE FROM history")

# ===============================================================================
#  Componentes Visuais Reutilizáveis — Padding, Bordas, Sombras e Botões (Flet)
# ===============================================================================

# ── Wrappers de ft.Padding / ft.Border / ft.BoxShadow — reduzem boilerplate nos layouts ──

def pad(a):
    return ft.Padding(left=a, top=a, right=a, bottom=a)

def padxy(x, y):
    return ft.Padding(left=x, right=x, top=y, bottom=y)

def padltrb(l, t, r, b):
    return ft.Padding(left=l, top=t, right=r, bottom=b)

def brd(color, w=1):
    return ft.border.all(w, color)

def brd_bottom(color, w=1):
    return ft.Border(bottom=ft.BorderSide(w, color))

def brd_top(color, w=1):
    return ft.Border(top=ft.BorderSide(w, color))

def brd_side(color, w=1):
    return ft.Border(
        left=ft.BorderSide(w, color),
        right=ft.BorderSide(w, color),
        bottom=ft.BorderSide(w, color))

def shd(color, blur=18):
    return ft.BoxShadow(blur_radius=blur, color=color, offset=ft.Offset(0, 4))


# ── Componentes de botão ─────────────────────────────────────────────────────────
def btn(label, on_click, *, bg, fg="#FFFFFF", bc=None, expand=1,
        h=None, fs=19, fw=ft.FontWeight.W_400, glow=None):

    bc      = bc or bg
    shd_val = (shd(glow, 20) if glow
               else ft.BoxShadow(blur_radius=10, color="#00000045",
                                 offset=ft.Offset(0, 4)))
    args = dict(
        content=ft.Text(label, color=fg, size=fs, weight=fw,
                        text_align=ft.TextAlign.CENTER, font_family="mono"),
        bgcolor=bg, border=brd(bc), border_radius=BTN_R,
        expand=expand,
        alignment=ft.Alignment(0, 0),
        on_click=on_click, ink=True, shadow=shd_val,
        animate=ft.Animation(60, ft.AnimationCurve.EASE_OUT),
    )
    if h is not None:
        args["height"] = h
    return ft.Container(**args)

def eq_btn(on_click, bg=None):
    
    bg = bg or C["btn_eq"]
    return ft.Container(
        content=ft.Text("=", color="#FFFFFF", size=26,
                        weight=ft.FontWeight.W_500, font_family="mono"),
        bgcolor=bg, border_radius=BTN_R,
        expand=1,
        alignment=ft.Alignment(0, 0),
        on_click=on_click, ink=True,
        shadow=shd(bg + "55", 24),
        animate=ft.Animation(60, ft.AnimationCurve.EASE_OUT),
    )

def row(*items):
    
    return ft.Row(list(items), spacing=6, expand=True)

def slbl(text, color=None):

    return ft.Container(
        content=ft.Text(text, size=10, color=color or C["text_second"],
                        weight=ft.FontWeight.W_700, font_family="mono"),
        padding=padltrb(2, 12, 2, 4),
    )

def gsep(c1=None, c2=None):

    return ft.Container(
        height=1, margin=ft.margin.symmetric(vertical=6),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
            colors=["transparent",
                    c1 or C["accent3"] + "60",
                    c2 or C["accent2"] + "60",
                    "transparent"]),
    )

def action_btn(label, on_click, color):

    return ft.Container(
        content=ft.Text(label, size=14, color="#FFFFFF",
                        font_family="mono", weight=ft.FontWeight.W_700),
        bgcolor=color, border_radius=BTN_R, height=56,
        alignment=ft.Alignment(0, 0),
        on_click=on_click, ink=True,
        shadow=shd(color + "50", 22),
    )

# ===============================================================================
#                              Função Principal
# ===============================================================================

def main(page: ft.Page):

    # ===========================================================================
    #                          Configuração da Página
    # ===========================================================================

    page.title      = CFG.title
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor    = C["bg"]
    page.scroll     = None
    page.fonts      = {"mono":
        "https://fonts.gstatic.com/s/jetbrainsmono/v18/"
        "tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjOVmNog.woff2"}
    page.theme   = ft.Theme(font_family="mono")
    page.padding = ft.padding.only(top=28, bottom=34)
    # top=28 : reserva espaço para a Status Bar (hora, bateria...)
    # bottom=34: reserva espaço para os Botões de Navegação (□ ○ ◁)

    # ===========================================================================
    #                     Persistência — Detecção de Plataforma
    # ===========================================================================

    def _get_support_dir() -> str:
        try:
            p = sys.platform
            if p == "android":
                d    = os.environ.get("ANDROID_DATA", "/data/data")
                base = os.path.join(d, "calc_tp1", "files")
            elif p == "ios":
                base = os.path.expanduser("~/Documents/calc_tp1")
            elif p == "win32":
                base = os.path.join(
                    os.environ.get("APPDATA", os.path.expanduser("~")),
                    "calc_tp1")
            elif p == "darwin":
                base = os.path.expanduser(
                    "~/Library/Application Support/calc_tp1")
            else:
                base = os.path.expanduser("~/.local/share/calc_tp1")
            os.makedirs(base, exist_ok=True)
            return base
        except Exception:
            return os.path.dirname(os.path.abspath(__file__))

    support_dir = _get_support_dir()
    db_path     = os.path.join(support_dir, "calc_history.db")

    # hist_db — instância de HistDB  (nome distinto de "db" = módulo duckdb)
    hist_db = HistDB(db_path, CFG.max_history)

    # ── Sincronização client_storage ─────────────────────────────────────────

    _CS_KEY = "calc_history_v2"

    def _sync_cs():
        
        # Sincroniza o client_storage com o conteúdo atual do banco de dados.
        try:
            page.client_storage.set(
                _CS_KEY,
                json.dumps(hist_db.fetch(), ensure_ascii=False, default=str))
        except Exception:
            pass

    # ── Restaurar de client_storage se DB ainda estiver vazio ────────────────

    try:
        if not hist_db.fetch():
            cs_raw = page.client_storage.get(_CS_KEY)
            if cs_raw:
                data = json.loads(cs_raw)
                for h in reversed(data):
                    if isinstance(h, dict) and "expression" in h and "result" in h:
                        try:
                            hist_db.insert(
                                h.get("mode", "Padrão"),
                                h["expression"][:256],
                                h["result"][:512])
                        except Exception:
                            pass
    except Exception:
        pass

    # ===========================================================================
    #                           Estado da Aplicação
    # ===========================================================================

    cur_mode  = [CFG.default_mode]
    hist_open = [False]
    parts: list[str] = []

    def get_expr():
        return "".join(parts)

    # ===========================================================================
    #                            Textos do Display
    # ===========================================================================

    txt_mode = ft.Text(
        CFG.default_mode.upper(), size=10, color=MODE_COLORS[CFG.default_mode],
        weight=ft.FontWeight.W_700, font_family="mono")

    txt_expr = ft.Text(
        "", size=14, color=UI["display_expr"],
        font_family="mono",
        text_align=ft.TextAlign.RIGHT,
        overflow=ft.TextOverflow.ELLIPSIS, max_lines=2)

    txt_result = ft.Text(
        "0", size=58, color=UI["display_main"],
        font_family="mono",
        text_align=ft.TextAlign.RIGHT,
        weight=ft.FontWeight.W_300,
        overflow=ft.TextOverflow.ELLIPSIS)

    txt_err = ft.Text(
        "", size=11, color=C["danger"],
        font_family="mono",
        text_align=ft.TextAlign.RIGHT,
        italic=True, visible=False)

    def set_ok(val, label=""):
        txt_result.value = val
        txt_result.color = UI["display_main"]
        txt_result.size  = 58 if len(val) < 10 else (42 if len(val) < 16 else 28)
        txt_err.visible  = False
        if label:
            txt_expr.value = _fmt_expr(label)
        page.update()

    def set_err(msg):
        txt_result.value = "Erro"
        txt_result.color = C["danger"]
        txt_result.size  = 36
        txt_err.value    = msg[:80]
        txt_err.visible  = True
        page.update()

    def reset():
        parts.clear()
        txt_expr.value   = ""
        txt_result.value = "0"
        txt_result.color = UI["display_main"]
        txt_result.size  = 58
        txt_err.visible  = False
        page.update()

    def upd():

        # Atualiza o display com a expressão atual formatada, mantendo o resultado e sem mostrar erros.
        txt_expr.value   = _fmt_expr(get_expr())
        txt_err.visible  = False
        txt_result.color = UI["display_expr"]
        page.update()

    # ===========================================================================
    #                    Layout Responsivo (Portrait / Landscape)
    # ===========================================================================

    # Alturas fixas dos elementos permanentes
    HEADER_H_PORT = 64 - 16  # altura do header em portrait (64) menos padding top+bottom (16)
    HEADER_H_LAND = 48
    TABBAR_H_PORT = 72
    TABBAR_H_LAND = 52
    SAFE_EXTRA    = 62   

    # Rácios para modo portrait
    DISPLAY_RATIO = 0.28
    KBD_RATIO     = 0.70

    # ── Display ──────────────────────────────────────────────────────────────────

    display_area = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=6, height=6,
                                     border_radius=ft.BorderRadius(3,3,3,3),
                                     bgcolor=MODE_COLORS[CFG.default_mode]),
                        txt_mode,
                    ], spacing=5),
                    bgcolor=C["accent_dim"],
                    border=brd(MODE_COLORS[CFG.default_mode] + "30"),
                    border_radius=ft.BorderRadius(20,20,20,20),
                    padding=padxy(10, 4),
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(expand=True),
            txt_expr,
            ft.Container(height=4),
            txt_result,
            txt_err,
            ft.Container(height=6),
        ], spacing=0, expand=True),
        bgcolor=UI["display_bg"],
        padding=padltrb(20, 10, 20, 0),
        height=200,
    )

    # ── Teclado ──────────────────────────────────────────────────────────────────

    kbd_inner_col = ft.Column(spacing=6, scroll=None)
    kbd_container = ft.Container(
        content=kbd_inner_col,
        bgcolor=UI["page_bg"],
        padding=padltrb(8, 4, 8, 4),
        height=400,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    # ── Lógica de orientação ─────────────────────────────────────────────────────

    _landscape = [False]

    def _is_landscape(pw, ph):
        return pw is not None and ph is not None and pw > ph

    def _calc_heights(pw: int, ph: int):

        landscape = _is_landscape(pw, ph)
        ph = max(ph, 200)
        if landscape:
            hdr_h = HEADER_H_LAND
            tab_h = TABBAR_H_LAND
            avail = max(ph - hdr_h - tab_h - SAFE_EXTRA, 120)
            d_h   = 0
            k_h   = avail
        else:
            hdr_h = HEADER_H_PORT
            tab_h = TABBAR_H_PORT
            avail = max(ph - hdr_h - tab_h - SAFE_EXTRA, 200)
            d_h   = int(avail * DISPLAY_RATIO)
            k_h   = avail - d_h - 6   # espaço restante após display + gap mínimo
        return d_h, k_h, landscape

    def _apply_heights(pw=None, ph=None):

        pw = pw or (page.width  if page.width  else 400)
        ph = ph or (page.height if page.height else 700)
        d_h, k_h, landscape = _calc_heights(int(pw), int(ph))
        _landscape[0] = landscape
        display_area.height  = d_h
        display_area.visible = (d_h > 0)

        if landscape:

            # Landscape: altura fixa px → overflow activado → scroll
            kbd_container.height = k_h
            kbd_container.expand = False
        else:

            # Portrait: altura fixa = k_h calculado por _calc_heights.
            # SAFE_EXTRA=62 desconta page.padding (28+34) do page.height.
            kbd_container.height = k_h
            kbd_container.expand = False

        # Scroll interno e alturas das rows
        if hasattr(kbd_container, "content") and kbd_container.content:
            if landscape:

                # Landscape: scroll activo, botões com altura fixa BTN_H_LAND
                kbd_container.content.scroll = ft.ScrollMode.ADAPTIVE
                kbd_container.content.expand = False
            else:

                if kbd_inner_col.controls:
                    kbd_col = kbd_inner_col.controls[0]
                    if hasattr(kbd_col, "controls") and kbd_col.controls:
                        rows = [c for c in kbd_col.controls
                                if isinstance(c, ft.Row)]
                        n  = len(rows)
                        sp = int(getattr(kbd_col, "spacing", 5) or 5)

                        # altura mínima total (+ 8px padding interno do container)
                        min_total = n * BTN_H_FN + max(0, n - 1) * sp + 8
                        if n > 0 and min_total <= k_h:

                            # ── CASO A ──────────────────────────────────────
                            kbd_container.content.scroll = None
                            kbd_container.content.expand = True
                            for row in rows:
                                row.height = None
                                row.expand  = True
                        else:

                            # ── CASO B ──────────────────────────────────────
                            kbd_container.content.scroll = ft.ScrollMode.ADAPTIVE
                            kbd_container.content.expand = False
                            for row in rows:
                                row.expand  = False   # obrigatório antes de scroll
                                row.height  = BTN_H

    # Guarda a última orientação para detectar rotação

    _last_landscape = [None]  # None = primeira inicialização

    def on_resize(e):

        pw = int(e.width)  if (hasattr(e, "width")  and e.width)  else (page.width  or 400)
        ph = int(e.height) if (hasattr(e, "height") and e.height) else (page.height or 700)
        _apply_heights(pw, ph)

        new_land = _landscape[0]
        if new_land != _last_landscape[0]:

            # Orientação mudou → rebuildar teclado com alturas correctas
            _last_landscape[0] = new_land
            rebuild_body(cur_mode[0])  # rebuild já chama page.update()
        else:
            page.update()

    page.on_resize = on_resize

    # ===========================================================================
    #                              Histórico
    # ===========================================================================

    hist_col      = ft.Column(spacing=0, scroll=ft.ScrollMode.ADAPTIVE)
    btn_hist_icon = ft.Icon(ft.Icons.HISTORY_ROUNDED, color=C["accent3"], size=18)

    def refresh_hist(mode=None):
        hist_col.controls.clear()
        entries = hist_db.fetch(mode)
        if not entries:
            hist_col.controls.append(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF_ROUNDED,
                            size=36, color=C["text_hint"]),
                    ft.Text("Sem histórico", size=13,
                            color=C["text_second"], font_family="mono",
                            text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=padxy(0, 24), alignment=ft.Alignment(0, 0)))
            page.update()
            return

        last_date = None
        for h in entries:
            eid = h["id"]
            ex  = h["expression"]
            rs  = h["result"]
            ts  = h["ts"]
            mc  = MODE_COLORS.get(h.get("mode", ""), C["accent"])

            try:
                dt_obj   = datetime.strptime(ts[:10], "%Y-%m-%d")
                cur_date = ts[:10]
                if cur_date != last_date:
                    last_date = cur_date
                    if dt_obj.date() == date.today():
                        date_lbl = "Hoje"
                    elif dt_obj.date() == date.today() - timedelta(days=1):
                        date_lbl = "Ontem"
                    else:
                        MESES = ["","janeiro","fevereiro","março","abril","maio",
                                 "junho","julho","agosto","setembro","outubro",
                                 "novembro","dezembro"]
                        date_lbl = f"{dt_obj.day} {MESES[dt_obj.month]}"
                        if dt_obj.year != date.today().year:
                            date_lbl += f" {dt_obj.year}"
                    hist_col.controls.append(ft.Container(
                        content=ft.Text(date_lbl, size=11,
                                        color=C["text_hint"], font_family="mono",
                                        weight=ft.FontWeight.W_600),
                        padding=padltrb(4, 14, 4, 4),
                    ))
            except Exception:
                pass

            def mk_recall(e_=ex, r_=rs):
                def _(ev):
                    parts.clear()
                    parts.append(e_)
                    txt_expr.value   = _fmt_expr(e_)
                    txt_result.value = r_
                    txt_result.color = UI["display_main"]
                    txt_result.size  = 42
                    txt_err.visible  = False
                    page.update()
                return _

            def mk_del(eid_=eid):
                def _(ev):
                    hist_db.delete(eid_)
                    _sync_cs()
                    refresh_hist(cur_mode[0])
                return _

            hist_col.controls.append(ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(ex[:44], size=12, color=C["text_second"],
                                font_family="mono",
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(rs, size=22, color=UI["display_main"],
                                font_family="mono",
                                weight=ft.FontWeight.W_400),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.REPLAY_ROUNDED,
                                            size=14, color=mc),
                            on_click=mk_recall(), width=30, height=30,
                            border_radius=ft.BorderRadius(15,15,15,15),
                            ink=True, bgcolor=mc + "18",
                            alignment=ft.Alignment(0, 0)),
                        ft.Container(
                            content=ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED,
                                            size=14, color=C["danger"]),
                            on_click=mk_del(), width=30, height=30,
                            border_radius=ft.BorderRadius(15,15,15,15),
                            ink=True, bgcolor=C["danger_dim"],
                            alignment=ft.Alignment(0, 0)),
                    ], spacing=4,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=10,
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="transparent",
                padding=padxy(4, 10),
                border=ft.Border(bottom=ft.BorderSide(1, C["border"])),
                on_click=mk_recall(), ink=True,
            ))
        page.update()

    hist_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY_ROUNDED,
                            color=C["accent3"], size=16),
                    ft.Text("HISTÓRICO", size=10, color=C["accent3"],
                            weight=ft.FontWeight.W_700, font_family="mono"),
                ], spacing=6),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text("LIMPAR", size=9, color=C["danger"],
                                    font_family="mono", weight=ft.FontWeight.W_700),
                    on_click=lambda e: (
                        hist_db.clear(cur_mode[0]),
                        _sync_cs(),
                        refresh_hist(cur_mode[0]),
                    ),
                    bgcolor=C["danger_dim"], border=brd(C["danger"] + "35"),
                    border_radius=ft.BorderRadius(8,8,8,8),
                    padding=padxy(10, 5), ink=True),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=4),
            hist_col,
        ], scroll=ft.ScrollMode.ADAPTIVE),
        bgcolor=C["surface"],
        border=brd_top(C["border_light"]),
        border_radius=ft.BorderRadius(0,0,0,0),
        padding=pad(14),
        visible=False, height=0,   # 0 quando fechado → não ocupa espaço
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    def toggle_hist(e):
        hist_open[0]       = not hist_open[0]
        hist_panel.visible = hist_open[0]
        hist_panel.height  = 360 if hist_open[0] else 0   # liberta espaço quando fechado
        btn_hist_icon.name = (ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED
                               if hist_open[0] else ft.Icons.HISTORY_ROUNDED)
        if hist_open[0]:
            refresh_hist(cur_mode[0])
        page.update()

    # ===========================================================================
    #                         Navegação — Tab Bar
    # ===========================================================================

    body_content = ft.Column(scroll=None, spacing=0, expand=True)
    tab_row      = ft.Row([], spacing=0)

    def build_tab_row():
        tabs = []
        for m in CFG.modes:
            mc     = MODE_COLORS[m]
            is_sel = m == cur_mode[0]
            tabs.append(ft.Container(
                content=ft.Column([
                    ft.Container(
                        height=2,
                        bgcolor=mc if is_sel else "transparent",
                        border_radius=ft.BorderRadius(0,0,2,2)),
                    ft.Container(
                        content=ft.Icon(MODE_ICONS[m],
                                        color=mc if is_sel else C["text_hint"],
                                        size=22),
                        width=44, height=28,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=mc + "20" if is_sel else "transparent",
                        border_radius=ft.BorderRadius(10,10,10,10)),
                    ft.Text(m, size=9,
                            color=mc if is_sel else C["text_hint"],
                            font_family="mono",
                            weight=(ft.FontWeight.W_700 if is_sel
                                    else ft.FontWeight.W_400),
                            text_align=ft.TextAlign.CENTER),
                ], spacing=3,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   tight=True),
                expand=True,
                on_click=lambda e, mn=m: switch_mode(mn),
                ink=True, padding=padxy(4, 6),
            ))
        tab_row.controls = tabs

    tab_bar = ft.Container(
        content=tab_row,
        bgcolor=C["surface"],
        border=brd_top(C["border_light"]),
        height=70, padding=padxy(6, 0),
        shadow=ft.BoxShadow(blur_radius=24, spread_radius=-4,
                            color=UI["shadow"], offset=ft.Offset(0, -4)),
    )

    def switch_mode(m):
        cur_mode[0]    = m
        txt_mode.value = m.upper()
        txt_mode.color = MODE_COLORS[m]
        parts.clear()
        reset()
        build_tab_row()
        rebuild_body(m)

    build_tab_row()

    # ===========================================================================
    #                           Modo 1 — Padrão
    # ===========================================================================

    def build_padrao():
        def dg(d): return lambda e: (parts.append(d), upd())
        def op(o): return lambda e: (parts.append(f" {o} "), upd())
        def clr(e): reset()

        def bk(e):
            if parts:
                l = parts[-1]
                if len(l) > 1: parts[-1] = l[:-1]
                else:          parts.pop()
            upd()

        def paren(e):
            expr  = get_expr()
            opens = expr.count("(") - expr.count(")")
            parts.append(")" if opens > 0 else "(")
            upd()

        def pct(e):
            v = get_expr().strip()
            if v:
                parts.clear()
                parts.append(f"({v})/100")
                upd()

        def eq(e):
            raw = get_expr().strip()
            if not raw: return
            try:
                r = calcular(raw)
                set_ok(r, f"{raw} =")
                hist_db.insert("Padrão", raw, r)
                _sync_cs()
                parts.clear()
                parts.append(r.replace("\u2009", ""))
            except ValueError as ve:
                set_err(str(ve))

        BD = C["btn_digit"]; BO = C["btn_op"]; BU = C["btn_util"]

        # Altura dos botões adaptativa por orientação:
        #   Portrait  → h=None + expand=True  (Row cresce para preencher)
        #   Landscape → h=BTN_H_LAND + expand=False (px fixo → overflow → scroll)

        land = _landscape[0]
        bh   = BTN_H_LAND if land else None

        def rw(*items):
            
            return ft.Row(list(items), spacing=6, expand=not land, wrap=False)

        def eb(on_click, bg=None):
            
            bg = bg or C["btn_eq"]
            return ft.Container(
                content=ft.Text("=", color="#FFFFFF", size=26,
                                weight=ft.FontWeight.W_500, font_family="mono"),
                bgcolor=bg, border_radius=BTN_R,
                expand=True, height=bh,
                alignment=ft.Alignment(0, 0),
                on_click=on_click, ink=True,
                shadow=shd(bg + "55", 24),
                animate=ft.Animation(60, ft.AnimationCurve.EASE_OUT),
            )

        # mk(key, handler, h=bh) → visual lido de BTN_SIMBOLS[key]

        return ft.Column([
            rw(mk("AC",  clr,     h=bh),
               mk("( )", paren,   h=bh),
               mk("%",   pct,     h=bh),
               mk("÷",   op("/"), h=bh)),
            rw(mk("7", dg("7"), h=bh), mk("8", dg("8"), h=bh),
               mk("9", dg("9"), h=bh), mk("×", op("*"), h=bh)),
            rw(mk("4", dg("4"), h=bh), mk("5", dg("5"), h=bh),
               mk("6", dg("6"), h=bh), mk("−", op("-"), h=bh)),
            rw(mk("1", dg("1"), h=bh), mk("2", dg("2"), h=bh),
               mk("3", dg("3"), h=bh), mk("+", op("+"), h=bh)),
            rw(mk("0", dg("0"), h=bh),
               mk(".", dg("."),  h=bh),
               mk("⌫", bk,      h=bh),
               eb(eq)),
        ], spacing=5, expand=not land)

    # ===========================================================================
    #                          Modo 2 — Científica
    # ===========================================================================

    def build_cientifica():
        def dg(d): return lambda e: (parts.append(d), upd())
        def op(o): return lambda e: (parts.append(f" {o} "), upd())
        def fn(f): return lambda e: (parts.append(f"{f}("), upd())
        def clr(e): reset()

        def bk(e):
            if parts:
                l = parts[-1]
                if len(l) > 1: parts[-1] = l[:-1]
                else:          parts.pop()
            upd()

        def paren(e):
            expr  = get_expr()
            opens = expr.count("(") - expr.count(")")
            parts.append(")" if opens > 0 else "(")
            upd()

        def pct(e):
            v = get_expr().strip()
            if v:
                parts.clear()
                parts.append(f"({v})/100")
                upd()

        def eq(e):
            raw = get_expr().strip()
            if not raw: return
            try:
                r = calcular(raw)
                set_ok(r, f"{raw} =")
                hist_db.insert("Científica", raw, r)
                _sync_cs()
                parts.clear()
                parts.append(r.replace("\u2009", ""))
            except ValueError as ve:
                set_err(str(ve))

        BF  = C["btn_fn"]
        TF  = C["text_fn"]
        BBF = C["accent3"] + "40"
        BD  = C["btn_digit"]
        BO  = C["btn_op"]
        BU  = C["btn_util"]

        # Altura adaptativa por orientação (mesmo padrão que Padrão)

        land  = _landscape[0]
        bh    = BTN_H_LAND if land else None
        bh_fn = max(BTN_H_LAND - 4, 38) if land else None  # funções ligeiramente mais baixas

        def rw(*items):
            return ft.Row(list(items), spacing=6, expand=not land, wrap=False)

        def eb(on_click, bg=None):
            bg = bg or C["btn_eq"]
            return ft.Container(
                content=ft.Text("=", color="#FFFFFF", size=26,
                                weight=ft.FontWeight.W_500, font_family="mono"),
                bgcolor=bg, border_radius=BTN_R,
                expand=True, height=bh,
                alignment=ft.Alignment(0, 0),
                on_click=on_click, ink=True,
                shadow=shd(bg + "55", 24),
                animate=ft.Animation(60, ft.AnimationCurve.EASE_OUT),
            )

        # mk(key, handler, h=…) → visual lido de BTN_SIMBOLS[key]
    
        return ft.Column([

            # ── Funções: 5 rows × 4 colunas - Row 1: Trigonométricas básicas ──────────────────────────────────
            rw(mk("sin",   fn("sin"),             h=bh_fn),
               mk("cos",   fn("cos"),             h=bh_fn),
               mk("tan",   fn("tan"),             h=bh_fn),
               mk("π",     dg("π"),               h=bh_fn)),

            # Row 2: Trigonométricas inversas + inversão
            rw(mk("asin",  fn("asin"),            h=bh_fn),
               mk("acos",  fn("acos"),            h=bh_fn),
               mk("atan",  fn("atan"),            h=bh_fn),
               mk("1/x",   lambda e: (parts.append("1/("), upd()), h=bh_fn)),

            # Row 3: Potência / raiz / logaritmos
            rw(mk("√",     fn("sqrt"),            h=bh_fn),
               mk("xⁿ",    lambda e: (parts.append("**"),  upd()), h=bh_fn),
               mk("log",   fn("log"),             h=bh_fn),
               mk("ln",    fn("ln"),              h=bh_fn)),

            # Row 4: Exponencial / fatorial / módulo / x²
            rw(mk("eˣ",    fn("exp"),             h=bh_fn),
               mk("n!",    lambda e: (parts.append("!"),   upd()), h=bh_fn),
               mk("|x|",   fn("Abs"),             h=bh_fn),
               mk("x²",    lambda e: (parts.append("**2"), upd()), h=bh_fn)),

            # Row 5: Arredondamento / parênteses individuais
            rw(mk("ceil",  fn("ceiling"),         h=bh_fn),
               mk("floor", fn("floor"),           h=bh_fn),
               mk("(",     dg("("),               h=bh_fn),
               mk(")",     dg(")"),               h=bh_fn)),

            # ── Grade numérica: 5 rows
            rw(mk("AC",  clr,     h=bh),
               mk("( )", paren,   h=bh),
               mk("%",   pct,     h=bh),
               mk("÷",   op("/"), h=bh)),
            rw(mk("7", dg("7"), h=bh), mk("8", dg("8"), h=bh),
               mk("9", dg("9"), h=bh), mk("×", op("*"), h=bh)),
            rw(mk("4", dg("4"), h=bh), mk("5", dg("5"), h=bh),
               mk("6", dg("6"), h=bh), mk("−", op("-"), h=bh)),
            rw(mk("1", dg("1"), h=bh), mk("2", dg("2"), h=bh),
               mk("3", dg("3"), h=bh), mk("+", op("+"), h=bh)),
            rw(mk("0", dg("0"), h=bh),
               mk(".", dg("."),  h=bh),
               mk("⌫", bk,      h=bh),
               eb(eq)),
        ], spacing=5, expand=not land)

    # ===========================================================================
    #                          Rebuild do Corpo Principal
    # ===========================================================================

    SCROLL_MODES = set()  # apenas modos button-based

    def rebuild_body(mode_name: str):
        txt_mode.value = mode_name.upper()
        txt_mode.color = MODE_COLORS[mode_name]
        kbd = {
            "Padrão":      build_padrao,
            "Científica":  build_cientifica,
        }[mode_name]()
        body_content.controls.clear()

        if mode_name in SCROLL_MODES:

            # Modos com conteúdo longo: scroll interno
            body_content.scroll = ft.ScrollMode.ADAPTIVE
            body_content.expand = True
            body_content.controls.append(
                ft.Column([
                    ft.Container(
                        content=ft.Column([
                            txt_expr,
                            ft.Container(height=4),
                            txt_result,
                            txt_err,
                        ], spacing=0),
                        bgcolor=UI["display_bg"],
                        padding=padltrb(20, 12, 20, 10),
                    ),
                    ft.Container(
                        content=kbd, bgcolor=UI["page_bg"],
                        padding=padltrb(10, 4, 10, 10)),
                    hist_panel,
                    ft.Container(height=8),
                ], spacing=0)
            )
        else:

            # Modos button-based: alturas px via _apply_heights
            body_content.scroll = None
            body_content.expand = True
            kbd_inner_col.controls.clear()
            kbd_inner_col.controls.append(kbd)
            _apply_heights()
            body_content.controls.append(display_area)
            body_content.controls.append(kbd_container)
            body_content.controls.append(hist_panel)

        page.update()

    # ===========================================================================
    #                                Header
    # ===========================================================================

    header = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.HISTORY_ROUNDED,
                                color=C["text_second"], size=22),
                width=44, height=44,
                border_radius=ft.BorderRadius(22,22,22,22),
                alignment=ft.Alignment(0, 0),
                on_click=toggle_hist, ink=True,
                bgcolor=C["surface"],
            ),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Row([
                    ft.Container(width=6, height=6,
                                 border_radius=ft.BorderRadius(3,3,3,3),
                                 bgcolor=MODE_COLORS[CFG.default_mode]),
                    txt_mode,
                ], spacing=5),
                bgcolor=C["surface"],
                border=brd(MODE_COLORS[CFG.default_mode] + "30"),
                border_radius=ft.BorderRadius(20,20,20,20),
                padding=padxy(12, 6),
            ),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Icon(ft.Icons.MORE_VERT_ROUNDED,
                                color=C["text_second"], size=22),
                width=44, height=44,
                border_radius=ft.BorderRadius(22,22,22,22),
                alignment=ft.Alignment(0, 0),
                ink=True, bgcolor=C["surface"],
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=UI["page_bg"],
        padding=padltrb(12, 10, 12, 10),
    )

    # ===========================================================================
    #                             Layout Principal
    # ===========================================================================

    _apply_heights(page.width, page.height)

    # page.padding.top/bottom reserva os insets do sistema (Status Bar + Nav Bar)
    page.add(ft.Column([
        header,
        ft.Container(
            content=body_content,
            expand=True,
            bgcolor=UI["page_bg"],
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        ),
        tab_bar,
    ], spacing=0, expand=True))

    rebuild_body(CFG.default_mode)


# ===============================================================================
#                               Ponto de Entrada
# ===============================================================================

ft.run(main, view=ft.AppView.FLET_BROWSER, port=8800)

