#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import schedule
import time



def main():
    # print("Initialising Scheduler.")
    # schedule.every(6).hours.do(lambda: os.system('python manage.py scrape'))
    # print("While loop.")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    #os.system("python manage.py scrape")
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockMarketAnalyzer.settings')
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
