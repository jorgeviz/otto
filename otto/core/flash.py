"""Convenience wrappers for flask.flash() with special-character handling.
"""

from flask import flash


def _escape(message):
    """Escape some characters in a message. Make them HTML friendly.

    Params:
    -----
    - message : (str) Text to process.

    Returns:
    - (str) Escaped string.
    """
    translations = {
        '"': '&quot;',
        "'": '&#39;',
        '`': '&lsquo;',
        '\n': '<br>',
        }
    for k, v in translations.items():
        message = message.replace(k, v)

    return message


def default(message):
    return flash(_escape(message), 'default')


def success(message):
    return flash(_escape(message), 'success')


def info(message):
    return flash(_escape(message), 'info')


def warning(message):
    return flash(_escape(message), 'warning')


def danger(message):
    return flash(_escape(message), 'danger')


def well(message):
    return flash(_escape(message), 'well')


def modal(message):
    return flash(_escape(message), 'modal')

