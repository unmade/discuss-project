import debug_toolbar

from .prod import *  # NOQA

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns
