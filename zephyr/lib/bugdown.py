import re
import markdown

# We need to re-initialize the markdown engine every 30 messages
# due to some sort of performance leak in the markdown library.
MAX_MD_ENGINE_USES = 30

_md_engine = None
_use_count = 0

# A link starts after whitespace, and cannot contain spaces,
# end parentheses, or end brackets (which would confuse Markdown).
# FIXME: Use one of the actual linkification extensions.
_link_regex = re.compile(r'(\s|\A)(?P<url>https?://[^\s\])]+)')

# Pad heading markers to make Markdown ignore them
# FIXME: Write a real extension for the markdown library
_heading_regex = re.compile(r'^([#-=])', flags=re.MULTILINE)

def _linkify(match):
    url = match.group('url')
    return ' [%s](%s) ' % (url, url)

def convert(md):
    """Convert Markdown to HTML, with Humbug-specific settings and hacks."""
    global _md_engine, _use_count

    if _md_engine is None:
        _md_engine = markdown.Markdown(
            extensions    = ['fenced_code', 'codehilite', 'nl2br'],
            safe_mode     = 'escape',
            output_format = 'xhtml')

    md = _heading_regex.sub(r' \1', md)
    md = _link_regex.sub(_linkify, md)

    try:
        html = _md_engine.convert(md)
    except:
        # FIXME: Do something more reasonable here!
        html = '<p>[Humbug note: Sorry, we could not understand the formatting of your message]</p>'

    _use_count += 1
    if _use_count >= MAX_MD_ENGINE_USES:
        _md_engine = None
        _use_count = 0

    return html
