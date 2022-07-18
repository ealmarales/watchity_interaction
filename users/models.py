from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from django.utils.translation import gettext as _

EXTERNAL_USERS_CHOICES = (
    ('SYSTEM', _('Sistem users')), # users with accounts in external API
    ('PARTICIPANT', _('Participant users')),  # users logged with email in external API

)
class InteractionUser(models.Model):
    """
    User model for interactions users.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    screen_name = models.CharField(_('screen name'), max_length=255)
    type = models.CharField(_('users type'), max_length=20, choices=EXTERNAL_USERS_CHOICES)

    def __str__(self):
        return self.user.__str__()
