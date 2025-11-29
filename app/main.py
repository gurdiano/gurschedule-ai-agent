import flet as ft
from template import Template

def main(page: ft.Page):
    page.title = "AI - Intelligent Study Assistant"
    page.window.width = 500
    page.window.height = 550

    template = Template(page)

    page.add(
        template
    )                                                               
ft.app(main)