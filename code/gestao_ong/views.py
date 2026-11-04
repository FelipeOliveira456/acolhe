from django.http import FileResponse, HttpResponse
from django.conf import settings


def spa(request):
    index = settings.BASE_DIR / 'static' / 'spa' / 'index.html'
    if not index.exists():
        return HttpResponse(
            'Interface ainda não gerada. Na pasta frontend, execute npm install e npm run build.',
            status=503,
        )
    return FileResponse(open(index, 'rb'))
