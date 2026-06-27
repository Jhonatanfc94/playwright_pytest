import imaplib
import email
import re
import os
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone


def get_otp_from_email(
    email_user: str,
    email_pass: str,
    retries: int = 10,
    delay: int = 5,
    sent_after: float | None = None,
    imap_host: str = "imap.gmail.com",
    subject_filter: str = "Verification code",
) -> str:
    """Connects to an IMAP server and extracts the OTP from the **latest**
    verification email that arrived **after** `sent_after` (epoch timestamp).

    Args:
        email_user: Email address.
        email_pass: Email app password (spaces are stripped automatically).
        retries: How many times to poll the inbox.
        delay: Seconds between retries.
        sent_after: Unix epoch timestamp. Only emails received *after* this
            moment are considered. If None, any email is accepted (legacy
            behaviour).
        imap_host: IMAP server hostname. Defaults to Gmail.
        subject_filter: Subject line to search for. Defaults to "Verification code".

    Returns:
        The OTP string (usually 6 digits).

    Raises:
        Exception: If no valid OTP email is found after all retries.
    """
    clean_pass = email_pass.replace(" ", "")

    for attempt in range(retries):
        mail = None
        try:
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(email_user, clean_pass)
            mail.select("inbox")

            # Search for specific verification email
            status, messages = mail.search(None, f'(SUBJECT "{subject_filter}")')
            if status != "OK" or not messages[0].split():
                print(f"[OTP] Attempt {attempt + 1}/{retries}: no emails found yet")
                mail.logout()
                time.sleep(delay)
                continue

            msg_nums = messages[0].split()

            # Walk emails from newest → oldest so we return the freshest OTP
            for msg_num in reversed(msg_nums):
                res, msg_data = mail.fetch(msg_num, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # ── Check email date against our "sent_after" marker ──
                if sent_after is not None:
                    email_date = msg.get("Date")
                    if email_date:
                        try:
                            email_dt = parsedate_to_datetime(email_date)
                            # Ensure both are UTC-aware for comparison
                            if email_dt.tzinfo is None:
                                email_dt = email_dt.replace(tzinfo=timezone.utc)
                            sent_after_dt = datetime.fromtimestamp(
                                sent_after, tz=timezone.utc
                            )
                            if email_dt < sent_after_dt:
                                # This email (and all older ones) arrived before
                                # we requested the OTP → skip the rest
                                print(
                                    f"[OTP] Skipping email dated {email_dt} "
                                    f"(before {sent_after_dt})"
                                )
                                break
                        except Exception:
                            pass  # If we can't parse the date, try anyway

                # ── Extract body ──
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type in ["text/plain", "text/html"]:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode(errors="ignore")
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")

                # Typically OTPs are 6 digits
                match = re.search(r"\b(\d{6})\b", body)
                if match:
                    otp = match.group(1)
                    print(f"[OTP] Found OTP: {otp} (attempt {attempt + 1})")
                    mail.logout()
                    return otp

                # Fallback: 4–8 digit codes
                match_fallback = re.search(r"\b(\d{4,8})\b", body)
                if match_fallback:
                    otp = match_fallback.group(1)
                    print(f"[OTP] Found OTP (fallback): {otp} (attempt {attempt + 1})")
                    mail.logout()
                    return otp

            mail.logout()
            print(
                f"[OTP] Attempt {attempt + 1}/{retries}: "
                "no fresh OTP email found, retrying..."
            )
            time.sleep(delay)

        except Exception as e:
            print(f"[OTP] Error on attempt {attempt + 1}: {e}")
            if mail:
                try:
                    mail.logout()
                except Exception:
                    pass
            time.sleep(delay)

    raise Exception("Failed to retrieve OTP from email after several attempts")
