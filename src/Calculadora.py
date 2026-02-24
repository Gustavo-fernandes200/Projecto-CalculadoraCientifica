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

# ===============================================================================
#                                     Configuração
# ===============================================================================
@dataclass(frozen = True)
class AppConfig:
  title : str = "Calculadora Cientifica"
  max_history : int = float('inf')
  modes : Tuple[str, ...] = ("Padrão","Científica","Gráfico","Programador")
  default_mode : str = "Padrão"
  live_preview: bool = False

  def validated(self) -> "AppConfig":
    mh = int(self.max_history)
    if mh < 1:
      mh = 1
    if mh > 'inf'
      mh = 'inf'
    
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

B = {
    ""
}