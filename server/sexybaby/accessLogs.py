from .models import AccessLogsModel
from pageScrape.models import Album
from django.conf import settings
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class AccessLogsMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):

        if not request.session.session_key:
            request.session.create()

        accessLogsData = dict()
        accessLogsData['path'] = request.path

        xForwardedFor = request.META.get('HTTP_X_FORWARDED_FOR')
        accessLogsData['ipAddress'] = xForwardedFor.split(
            ',')[0] if xForwardedFor else request.META.get('REMOTE_ADDR')

        accessLogsData['method'] = request.method
        accessLogsData['referrer'] = request.META.get('HTTP_REFERER', None)
        accessLogsData['session_key'] = request.session.session_key

        data = dict()
        data['get'] = dict(request.GET.copy())
        data['post'] = dict(request.POST.copy())

        keysToBeRemoved = ['password', 'csrfmiddlewaretoken']
        for key in keysToBeRemoved:
            data['post'].pop(key, None)

        accessLogsData['data'] = data
        accessLogsData['timestamp'] = timezone.now()

        # AccessLogsModel(**accessLogsData).save()

        response = self.get_response(request)
        return response
