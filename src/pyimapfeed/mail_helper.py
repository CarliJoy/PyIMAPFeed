from django.utils.html import escape
from imap_tools import MailMessage


def get_html_display(mail: MailMessage) -> str:
    """
    Generate a HTML Representation of a Mail content

    Args:
        mail:

    Returns:
        HTML representation
    """
    if mail.html:
        return mail.html
    else:
        return (
            "<html><body><b>Text Only Mail</b><pre>"
            + escape(mail.text)
            + "</pre></html></body>"
        )
