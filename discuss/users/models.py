from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(models.Model):
    username = models.CharField(_('Username'), max_length=150, unique=True)
    email = models.EmailField(_('Email address'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username
