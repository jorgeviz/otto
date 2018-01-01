"""Convenience functions for sending email from any view or Celery task."""

import hashlib
from logging import getLogger
from flask import current_app
from flask_mail import Message
from werkzeug.debug import tbtools
import datetime

logger = getLogger(__name__)

"""Redis keys used for entire application emails.
"""
# Email throttling
EMAIL_THROTTLE = 'otto:email_throttle:{md5}'  # Lock.


def send_email(subject, body=None, html=None, recipients=None, throttle=None):
    """Send an email. Optionally throttle the amount an identical email goes out.

    If the throttle argument is set, an md5 checksum derived from the subject, body, html, and recipients is stored in
    Redis with a lock timeout. On the first email sent, the email goes out like normal. But when other emails with the
    same subject, body, html, and recipients is supposed to go out, and the lock hasn't expired yet, the email will be
    dropped and never sent.

    Params:
    -----
    - subject : (str) the subject line of the email.
    - body : (str) the body of the email (no HTML).
    - html : (str) the body of the email, can be HTML (overrides body).
    - recipients : (list) email addresses to send the email to. Defaults to the ADMINS list in the
        Flask config.
    - throttle (int | datetime.timedelta) time in seconds or datetime.timedelta object between sending identical emails.
    """
    recipients = recipients or current_app.config['ADMINS']
    if isinstance(throttle, int) or isinstance(throttle, datetime.timedelta):
        md5 = hashlib.md5('{}{}{}{}'.format(subject, body, html, recipients)).hexdigest()
        seconds = throttle.total_seconds() if hasattr(throttle, 'total_seconds') else throttle
        lock = redis.lock(EMAIL_THROTTLE.format(md5=md5), timeout=int(seconds))
        have_lock = lock.acquire(blocking=False)
        if not have_lock:
            logger.debug('Suppressing email: {}'.format(subject))
            return
    msg = Message(subject=subject, recipients=recipients, body=body, html=html)
    mail.send(msg)
    logger.info("Sent email!")
