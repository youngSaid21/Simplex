# custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_last_digit(value):
    # Assurez-vous que la valeur est une chaîne
    value = str(value)
    # Récupérez le dernier caractère de la chaîne
    last_digit = int(value[-1]) + 1
    return last_digit
