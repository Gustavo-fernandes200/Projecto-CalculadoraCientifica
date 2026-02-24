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
import sympy as sp
from sympy import(sqrt, log, sin, cos, tan, asin, acos, atan, pi, E, factorial, 
                  Abs, ceilling, floor )
from dataclasses import field
from dataclasses import dataclass
from duckdb import datetime, date, timedelta
from math
from functools import lru_cache
from typing import Tuple

# ===============================================================================
#                                     Configuração
# ===============================================================================
@dataclass(frozen = True)
class AppConfig:
  title : str = "Calculadora Cientifica"
  max_history : int = float('inf') #infinito
  modes : Tuple[str, ...] = ("Padrão","Científica","Gráfico","Programador")
  default_mode : str = "Padrão"
  live_preview: bool = False

  def validated(self) -> "AppConfig":
    mh = int(self.max_history)
    if mh < 1:
      mh = 1
    if mh > ('inf')
      mh = ('inf') 
    
    dm = self.default_mode if self.default_mode in self.modes else "Padrão"
    return AppConfig(
      title = self.title,
      max_history = mh,
      modes = self.modes,
      default_mode = dm,
      live_preview = bool (self.live_preview),
    )
    
CFG = AppConfig().validated()
# ===============================================================================
#                               Configuração de Cores 
# ===============================================================================

C = {
    "bg"          : "#0A0E1A",
    "surface"     : "#111827",
    "surface2"    : "#1C2333",
    "glass"       : "#151C2E",
    "card"        : "#161E30",
    "card2"       : "#1A2540",
    "border"      : "#232E45",
    "border_light": "#2E3C58",
    "btn_digit"   : "#1A2235",
    "btn_op"      : "#1E1438",
    "btn_fn"      : "#0D1C2E",
    "btn_extra"   : "#181F35",
    "btn_prog"    : "#1A1610",
    "btn_clear"   : "#2A1015",
    "accent"      : "#00D4A0",
    "accent_dim"  : "#00D4A015",
    "accent2"     : "#8B5CF6",
    "accent2_dim" : "#8B5CF615",
    "accent3"     : "#38BDF8",
    "accent3_dim" : "#38BDF815",
    "accent4"     : "#FBBF24",
    "accent4_dim" : "#FBBF2415",
    "accent5"     : "#F472B6",
    "accent5_dim" : "#F472B615",
    "danger"      : "#F87171",
    "danger_dim"  : "#F8717115",
    "text_primary": "#EFF2F7",
    "text_second" : "#5A6882",
    "text_hint"   : "#3A4A64",
    "text_fn"     : "#38BDF8",
    "text_op"     : "#B09FFF",
    "text_eq"     : "#001A14",
    "btn_eq"      : "#00D4A0",
}

MODE_COLORS = {
    "Padrão":      C["accent"],
    "Científica":  C["accent3"],
    "Gráfica":     C["accent2"],
    "Programador": C["accent4"],
    "Data":        C["accent5"],
}

UI = {
  "page_bg": C["bg"],
  "display_bg" : C["bg"],
  "display_main" : C["text_primary"],
  "display_expr" : C["text_second"],
  "key_bg" : C["surface2"],
  "key_text" : C["text_primary"],
  "mem_text" : C["text_second"],
  "op_text": C["accent3"],
  "eq_bg": C["accent3"],
  "eq_text": "#FFFFFF",
  "top_btn_bg": C["surface2"],
  "top_btn_icon": C["text_primary"],
  "shadow": "#00000090",
}

MODE_ICONS = {
    "Padrão":      ft.Icons.CALCULATE_ROUNDED,
    "Científica":  ft.Icons.FUNCTIONS_ROUNDED,
    "Gráfica":     ft.Icons.SHOW_CHART_ROUNDED,
    "Programador": ft.Icons.DATA_OBJECT_ROUNDED,
    "Data":        ft.Icons.DATE_RANGE_ROUNDED,
}