# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re

from froide.settings import Base, ThemeBase, German


def rec(x):
    return re.compile(x, re.I | re.U)


def gettext(s):
    return s


class FragDenStaatBase(German, ThemeBase, Base):

    LANGUAGES = (
        ('de', gettext('German')),
    )

    FROIDE_THEME = 'fragdenstaat_de.theme'

    @property
    def INSTALLED_APPS(self):
        installed = super(FragDenStaatBase, self).INSTALLED_APPS
        installed += [
            'celery_haystack',
            'djcelery_email',
            'django.contrib.redirects',
            'tinymce',
            'django_filters',
            'markdown_deux',
            'raven.contrib.django.raven_compat',
            'froide_campaign.apps.FroideCampaignConfig',
            'froide_legalaction.apps.FroideLegalActionConfig',
        ]
        return installed

    @property
    def GEOIP_PATH(self):
        return os.path.join(super(FragDenStaatBase,
                            self).PROJECT_ROOT, '..', 'data')

    TINYMCE_DEFAULT_CONFIG = {
        'plugins': "table,spellchecker,paste,searchreplace",
        'theme': "advanced",
        'cleanup_on_startup': False
    }

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'froide.helper.middleware.XForwardedForMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'fragdenstaat_de.theme.ilf_middleware.CsrfViewIlfMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
        'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
        'froide.account.middleware.AcceptNewTermsMiddleware',
    ]

    CACHES = {
        'default': {
            'LOCATION': 'unique-snowflake',
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }

    # ######## Celery Haystack ########
    # Experimental feature to update index after 60s
    CELERY_HAYSTACK_COUNTDOWN = 60

    # ######### Debug ###########

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        }
    }
    HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

    SITE_NAME = "FragDenStaat"
    SITE_EMAIL = "info@fragdenstaat.de"
    SITE_URL = 'http://localhost:8000'

    SECRET_URLS = {
        "admin": "admin",
    }

    ALLOWED_HOSTS = ('*',)
    ALLOWED_REDIRECT_HOSTS = ('*',)

    DEFAULT_FROM_EMAIL = 'info@fragdenstaat.de'
    EMAIL_SUBJECT_PREFIX = '[AdminFragDenStaat] '

    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
    CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    CELERY_EMAIL_TASK_CONFIG = {
        'max_retries': None,
        'ignore_result': False,
        'acks_late': True,
        'store_errors_even_if_ignored': True
    }

    # Fig broker setup
    if 'BROKER_1_PORT' in os.environ:
        CELERY_BROKER_PORT = os.environ['BROKER_1_PORT'].replace('tcp://', '')
        BROKER_URL = 'amqp://guest:**@%s/' % CELERY_BROKER_PORT

    @property
    def FROIDE_CONFIG(self):
        config = super(FragDenStaatBase, self).FROIDE_CONFIG
        config.update(dict(
            create_new_publicbody=False,
            publicbody_empty=True,
            user_can_hide_web=True,
            public_body_officials_public=False,
            public_body_officials_email_public=False,
            default_law=2,
            doc_conversion_binary="/usr/bin/libreoffice",
            dryrun=False,
            dryrun_domain="test.fragdenstaat.de",
            allow_pseudonym=True,
            api_activated=True,
            have_newsletter=True,
            search_engine_query='http://www.google.de/search?as_q=%(query)s&as_epq=&as_oq=&as_eq=&hl=en&lr=&cr=&as_ft=i&as_filetype=&as_qdr=all&as_occt=any&as_dt=i&as_sitesearch=%(domain)s&as_rights=&safe=images',
            show_public_body_employee_name=False,
            request_throttle=[
                (5, 5 * 60),  # 2 requests in 5 minutes
                (30, 7 * 24 * 60 * 60),  # 15 requests in 7 days
            ],
            greetings=[
                rec(r"Sehr geehrt(er? (?:Herr|Frau)(?: ?Dr\.?)?(?: ?Prof\.?)? .*)"),
            ],
            custom_replacements=[
                rec(r'[Bb][Gg]-[Nn][Rr]\.?\s*\:?\s*([a-zA-Z0-9\s/]+)')
            ],
            closings=[rec(r"([Mm]it )?(den )?(freundliche(n|m)?|vielen|besten)? ?Gr(ü|u)(ß|ss)(en?)?,?"), rec("Hochachtungsvoll,?"), rec(r'i\. ?A\.'), rec('[iI]m Auftrag')]
        ))
        return config
