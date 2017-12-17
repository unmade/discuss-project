from .prod import *  # NOQA

import debug_toolbar

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns
