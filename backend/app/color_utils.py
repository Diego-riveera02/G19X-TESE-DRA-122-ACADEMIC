"""Utilidades auxiliares de visualizacion."""


def get_color(estado):
    if estado == "Critico": return "#E63946"
    if estado == "Alerta": return "#D4A017"
    return "#4BB543"
