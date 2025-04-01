from django import template
import re

register = template.Library()


@register.filter
def phone_link(phone_number):
    """
    Converts a phone number into a clickable 'tel:' link.
    Strips characters like (), -, and spaces.
    """
    if phone_number:
        stripped_number = re.sub(r"[()\-\s]", "", phone_number)
        return f'<a href="tel:{stripped_number}" title="call: {phone_number}">{phone_number}</a>'
    return phone_number
