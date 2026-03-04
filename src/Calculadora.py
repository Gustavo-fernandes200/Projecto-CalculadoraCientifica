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
  title : str = "Calculadora Cientifica"
  max_history : Union[int,float] = float('inf') #infinito
  modes : Tuple[str, ...] = ("Padrão","Científica")
  default_mode : str = "Padrão"
  live_preview: bool = False

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

# ===============================================================================
#                               Configuração de Botões
# ===============================================================================

BTN_SIMBOLS = {

    # ── Digitos Numericos ─────────────────────────────────────────────

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
    "."    : {"bg": C["btn_digit"],                              "fs": 26, "fw": ft.FontWeight.W_700},

    # ── Operadores ──────────────────────────────────────────────────────────────────────────────────────────

    "+"    : {"bg": C["btn_op"],                                 "fs": 22},
    "-"    : {"bg": C["btn_op"],                                 "fs": 22},
    "x"    : {"bg": C["btn_op"],                                 "fs": 22},
    "/"    : {"bg": C["btn_op"],                                 "fs": 22},
    "^"    : {"bg": C["btn_op"],                                 "fs": 22},

    # ── Utilitários (AC / parênteses / percentagem / retrocesso) ─────────────────────────────────────────────
    
    "AC"    : {"bg": C["btn_util"],  "fs": 17, "fw": ft.FontWeight.W_700, "glow": C["btn_util"] + "35"},
    "( )"   : {"bg": C["btn_util"],  "fs": 15},
    "%"     : {"bg": C["btn_util"],  "fs": 18},
    "⌫"    : {"bg": C["btn_digit"], "fs": 20},

    # ── Funções Cientificas - Trigonométrica Básica ──────────────────────────────────────────────────────────────────────────────── 
    
    "sin"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "cos"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "tan"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    
    # ── Funções Cientificas - Trigonométrica Inversa ────────────────────────────────────────────────────────────────────────────────
    
    "asin"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    "acos"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    "atan"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 11},
    
    # ── Constantes π  ────────────────────────────────────────────────────────────────────────────────
    
    "π"    : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 18},
    "e"    : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 18},
    
    # ── Inversão e Potencias  ────────────────────────────────────────────────────────────────────────────────

    "1/x"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "√"    : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 15},
    "xⁿ"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "x²"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},

    # ── Logaritmos e Exponencial ────────────────────────────────────────────────────────────────────────────────
    
    "log"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "ln"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "eˣ"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    
    # ── Fatorial e Módulo ────────────────────────────────────────────────────────────────────────────────    

    "n!"   : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "mod"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 13},
    "|x|"  : {"bg": C["btn_fn"], "fg": C["text_fn"], "bc": C["accent3"] + "40", "fs": 12},
}

def mk(key: str, handler, *, h=None, bg=None, fg=None) -> ft.Container:

    cfg = BTN_SIMBOLS[key]
    label = "C" if key == "C_p" else key
    return btn(

        label, handler,
        bg   = bg or cfg["bg"],
        fg   = fg or cfg.get("fg", "#FFFFFF"),
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

_NS_SYMPY = {

    "sqrt" :sqrt, "log"     :log,     "ln"         :log,
    "sin"  :sin,  "cos"     :cos,     "tan"        :tan,
    "asin" :asin, "acos"    :acos,    "atan"       :atan,
    "Abs"  :Abs,  "ceiling" :ceiling, "floor"      :floor,
    "pi"   :pi,   "E"       :E,       "factorial"  :factorial, 
    "exp"  :sp.exp,
}

_FAST_NS: dict = {
    "__builtins__": {}, # bloqueia acesso a builtins para segurança e evitar uso indevido

    # Funções Trigonométricas e Inversas 
    "sin" :   math.sin,   "cos" :   math.cos,   "tan" :   math.tan,
    "asin":   math.asin,  "acos":   math.acos,  "atan":   math.atan,

    # Logaritmos, Potencias e Raizs
    "sqrt"     :  math.sqrt,  "log"  :   math.log,   "log10": math.log10,
    "exp"      :  math.exp,   "abs"  :   abs,
    "ceil"     :  math.ceil,  "floor":   math.floor,
    "factorial":  math.factorial,

    # Constantes
    "pi":    math.pi,    "e":     math.e,     "E":     math.e,

}

# ── Mapeamento de expressões compiladas para verficação rápida  ─────────────────────────────────────────────

__RE_FACTORIAL = re.compile(r"(\d+)!")
__RE_SUBS: list[Tuple[re.Pattern, str]] = [
    
    (re.compile(r"\bsqrt\b"),  "sqrt"),
    (re.compile(r"\bln\b"),    "ln"),
    (re.compile(r"\blog\b"),   "log"),
    (re.compile(r"\bsin\b"),   "sin"),
    (re.compile(r"\bcos\b"),   "cos"),
    (re.compile(r"\btan\b"),   "tan"),
    (re.compile(r"\basin\b"),  "asin"),
    (re.compile(r"\bacos\b"),  "acos"),
    (re.compile(r"\batan\b"),  "atan"),
    (re.compile(r"\babs\b"),   "abs"),
    (re.compile(r"\bceil\b"),  "ceiling"),
    (re.compile(r"\bfloor\b"), "floor"),
    (re.compile(r"\bexp\b"),   "exp"),
    (re.compile(r"π"),         "pi"),
    (re.compile(r"x"),          "*"),
    (re.compile(r"÷"),          "/"),
    (re.compile(r"\^"),          "**"),
]

# ── Núcleo do Motor de Cálculo  ─────────────────────────────────────────────

# ---- Arquitetura de Velocidade de Cálculo - Nivel 1 -------------------------------
@lru_cache(maxsize = 4096) # cache de resultados para acelerar cálculos repetidos
def eval_expr(expr: str) -> str:

    # "Abs(" → "abs(" para compatibilidade com _FAST_NS e segurança (evita acesso a 
    # builtins e outros nomes potencialmente perigosos)
    e = expr.replace("Abs(", "abs(").replace("ceiling(", "ceil(")
    v = eval(e, _FAST_NS)
    
    if not isinstance(v, (int, float, complex)):
        raise TypeError("Resultado não numérico")
    f = float(v)

    if not math.isfinite(f):
        raise ValueError("Resultado indefinido.")
    return _fmt(int(f) if f == int(f) else f)

# ---- Arquitetura de Velocidade de Cálculo - Nivel 2 -------------------------------
@lru_cache(maxsize = 512) # cache de expressões compiladas para acelerar cálculos complexos
def _eval_expr(expr: str) -> str:

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
    
    # Normalização básica de expressões para compatibilidade com o motor de cálculo e melhor legibilidade
    e = expr.strip()
    e = e.replace("^",  "**")
    e = e.replace("π",  "pi")
    e = e.replace("×",  "*")
    e = e.replace("÷",  "/")
    e = e.replace("−",  "-")

    # Número no início de token + letra/( → * -> (?<![a-zA-Z0-9]) garante que não apanha dígitos dentro de identificadores
    # como "log10" (onde "0" é precedido de "1" que é precedido de "g")
    e = re.sub(r"(?<![a-zA-Z0-9])(\d+)([a-zA-Z(])", r"\1*\2", e)

    # "pi" + letra/( → * -> (?<![a-zA-Z]) garante que "pi" não seja parte de um identificador maior como "pippo"
    e = re.sub(r"(?<![a-zA-Z])(pi)(?=[a-zA-Z(])", r"\1*", e)

    # "e" isolado (constante de Euler) + letra/( → * -> (?<![a-zA-Z]) garante que "e" seja isolado e não parte de um identificador maior como "exp" ou "euler")
    e = re.sub(r"\b(e)\b(?=[a-zA-Z(])", r"\1*", e)

    # Fecho ) + letra/( → * -> \)(?=[a-zA-Z(]) garante que o ) seja seguido de letra ou ( sem espaço, indicando multiplicação implícita
    e = re.sub(r"\)([a-zA-Z(])", r")*\1", e)

    return e

# ===============================================================================
#                               Historico de Cálculos
# ===============================================================================
 
class HistDB:
    def __init__(self, db_path: str, max_history: Union[int, float] = 200):
        self.db_path = str(db_path)
        self.max_history = max_history

        # Garante que a pasta existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # CORREÇÃO: como importaste "duckdb as db", tens de usar db.connect(...)
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

        # Se for infinito (ou None), não faz trim
        if mh is None:
            return
        if isinstance(mh, float) and math.isinf(mh):
            return

        mh = int(mh)
        if mh < 1:
            mh = 1

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
#          Construção de Layout — Padding, Bordas, Sombras e Botões (Flet)
# ===============================================================================

# ── Construção dos botões em elementos de UI ───────────────────────────────────────────────────────── 

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

# ── Criação da estrutura grafica dos Botões ─────────────────────────────────────────────────────────

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

def eq_bar(on_click, bg=None):
    
    bg = bg or C["btn_eq"]
    return ft.Row([ft.Container(
        content=ft.Text("=", color="#FFFFFF", size=26,
                        weight=ft.FontWeight.W_500, font_family="mono"),
        bgcolor=bg, border_radius=BTN_R,
        expand=True,
        alignment=ft.Alignment(0, 0),
        on_click=on_click, ink=True,
        shadow=shd(bg + "55", 24),
    )], expand=True)

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

async def main(page: ft.Page):
    storage_paths = ft.StoragePaths()

    items = []
    for label, method in [
        ("Application cache directory", storage_paths.get_application_cache_directory),
        (
            "Application documents directory",
            storage_paths.get_application_documents_directory,
        ),
        (
            "Application support directory",
            storage_paths.get_application_support_directory,
        ),
        ("Downloads directory", storage_paths.get_downloads_directory),
        ("External cache directories", storage_paths.get_external_cache_directories),
        (
            "External storage directories",
            storage_paths.get_external_storage_directories,
        ),
        ("Library directory", storage_paths.get_library_directory),
        ("External storage directory", storage_paths.get_external_storage_directory),
        ("Temporary directory", storage_paths.get_temporary_directory),
        ("Console log filename", storage_paths.get_console_log_filename),
    ]:
        try:
            value = await method()
        except ft.FletUnsupportedPlatformException as e:
            value = f"Not supported: {e}"
        except Exception as e:
            value = f"Error: {e}"
        else:
            if isinstance(value, list):
                value = ", ".join(value)
            elif value is None:
                value = "Unavailable"

        items.append(
            ft.Text(
                spans=[
                    ft.TextSpan(
                        f"{label}: ", style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                    ),
                    ft.TextSpan(value),
                ]
            )
        )

    page.add(ft.Column(items, spacing=5))



if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP)