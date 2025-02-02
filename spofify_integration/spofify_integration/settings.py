"""
Django settings for spofify_integration project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-1hy!_h3+j4)zvm10jp2u)#ph=$rw%)@))t0kz3+&kyczfs+$gj"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "spofify_integration",  # Ensure this matches your app name
    "debug_toolbar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    # Required for Django Debug Toolbar to work locally
    "127.0.0.1",
]

ROOT_URLCONF = "spofify_integration.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(
                BASE_DIR, "spofify_integration", "templates", "spotify_templates"
            )
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "spofify_integration.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_creds_loaded = False


def get_env_var(env_var_name: str) -> str:
    """
    Retrieves the value of an environment variable from a creds.env file
    located two directories above the current script.

    Args:
        env_var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the environment variable, or None if not found.
    """
    global _creds_loaded

    creds_file: Path = Path(__file__).parent.parent.parent.joinpath(
        "creds.env",
    )

    # Load the creds.env file if it hasn't already been loaded
    if not _creds_loaded:
        if creds_file.exists():
            load_dotenv(dotenv_path=creds_file)
            _creds_loaded = True
        else:
            raise FileNotFoundError(f"The file '{creds_file}' does not exist.")

    # Retrieve and return the environment variable value
    value = os.getenv(key=env_var_name)
    if value is None:
        raise ValueError(
            f"The environment variable '{env_var_name}' was not found in '{creds_file}'."
        )
    return value


SPOTIFY_CLIENT_ID: str = get_env_var(env_var_name="SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET: str = get_env_var(env_var_name="SPOTIFY_CLIENT_SECRET")
