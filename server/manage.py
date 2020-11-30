#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from sexybaby import settings


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sexybaby.settings')
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

    params = sys.argv
    if params[1] == 'scrape':
        if params[2] == 'kissgoddess':
            from pageScrape import kissgoddess
            kissgoddess.main()
        if params[2] == 'hotgirlbiz':
            from pageScrape import hotgirlbiz
            hotgirlbiz.main()

    if params[1] == 'run-script':
        if params[2] == 'kissgoddess':
            from pageScrape import kissgoddess
            kissgoddess.main()
        if params[2] == 'hotgirlbiz':
            from pageScrape import hotgirlbizUtils
            hotgirlbizUtils.checkifthumbnailexistandFix()
    main()
