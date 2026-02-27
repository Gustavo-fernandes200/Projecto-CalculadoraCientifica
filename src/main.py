import flet as ft
from Calculadora import CFG, C, UI, MODE_COLORS, MODE_ICONS


def main(page: ft.Page):
    page.title = CFG.title
    page.bgcolor = C["bg"]
    page.padding = 0

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                expand=True,
                bgcolor=C["bg"],
                content=ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=ft.Padding.all(20),
                            content=ft.Text(
                                CFG.title,
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=C["text_primary"],
                            ),
                        ),
                        ft.Container(
                            padding=ft.Padding.all(20),
                            content=ft.Text(
                                "Calculadora Científica — em desenvolvimento",
                                size=16,
                                color=C["text_second"],
                            ),
                        ),
                    ],
                ),
            ),
        )
    )


ft.run(main, host="0.0.0.0", port=5000, view=ft.AppView.WEB_BROWSER)
