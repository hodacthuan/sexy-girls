from pageScrape import hotgirlbiz


def my_scheduled_job():
    print('This cron job is running')
    hotgirlbiz.prodPageScrape()

    pass
