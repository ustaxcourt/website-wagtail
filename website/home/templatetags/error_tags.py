from django import template
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.tag(name="safe_block")
def do_safe_block(parser, token):
    """
    A template tag that catches and logs exceptions during rendering.

    Usage:
    {% safe_block %}
        ... template code that might fail ...
    {% endsafe_block %}
    """
    nodelist = parser.parse(("endsafe_block",))
    parser.delete_first_token()
    return SafeNode(nodelist)


class SafeNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        try:
            return self.nodelist.render(context)
        except Exception as e:
            logger.warning("Error rendering block in safe_block: %s", e, exc_info=True)
            return f'<div class="error-message" style="color: red; border: 1px solid red; padding: 10px;">Template rendering error: {e}</div>'
