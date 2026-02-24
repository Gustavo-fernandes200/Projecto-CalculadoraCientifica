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

  def validated(self) -> "App-config"

# ===============================================================================
#                               Configuração de Cores 
# ===============================================================================

B = {
    ""
}