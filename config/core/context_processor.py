from django.conf import settings


def general(request):
    global_link=settings.LINK_ALL_CONNECT

    return dict(global_link=global_link)
