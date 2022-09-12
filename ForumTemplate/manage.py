#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

'''
    A web-forum powered by the Django framework, developed in Python using the
    pipenv virtual environment.
    
    Features include a user authentication system with encrypted password protection,
    subforums, threads, posts, quotation boxes to highlight existing posts
    replies, tags for custom font styles, embedded links, youtube videos
'''

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ForumTemplate.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
