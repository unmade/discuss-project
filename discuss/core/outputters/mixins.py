from datetime import datetime

from django.http import StreamingHttpResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from .base import Outputter


class OutputMixin(object):
    outputter_class = Outputter
    default_output_format = 'xml'
    filename_prefix = ''

    def get(self, request, *args, **kwargs):
        outputter = self.outputter_class()

        output_format = request.GET.get('output', self.default_output_format)
        if output_format not in outputter.outputters:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'error': _(f'Unsupported output format.')}
            )

        queryset = self.filter_queryset(self.get_queryset())

        response = StreamingHttpResponse(
            outputter.output(output_format, queryset),
            content_type=outputter.mimetypes[output_format]
        )

        filename = f'{self.filename_prefix}{datetime.now()}.{output_format}'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
