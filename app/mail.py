#!/usr/bin/python3
"""Utility functions for sending emails"""
from mailjet_rest import Client
import os


API_KEY = os.environ.get('MAILJET_API_KEY')
API_SECRET = os.environ.get('MAILJET_API_SECRET')

mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')


def send_email(to, subject, text, html):
    """
    Send an email.
    
    :param to: Recipient email address.
    :param subject: Email subject.
    :param template: Email body content.
    """
    data = {
      'Messages': [
        {
          "From": {
            "Email": "info@shamshar.online",
            "Name": "GuideAndSeek"
          },
          "To": [
            {
              "Email": to,
              "Name": "You"
            }
          ],
          "Subject": subject,
          "TextPart": text,
          "HTMLPart": html
        }
      ]
    }
    result = mailjet.send.create(data=data)
    if result.status_code != 200:
      print(f"Failed to send email. Status code: {result.status_code}, Error: {result.json()}")
    is_sent = result.status_code == 200
    return is_sent
