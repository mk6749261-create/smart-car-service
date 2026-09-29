from rest_framework.routers import DefaultRouter

from .views import ServiceViewSet

app_name = "services"

router = DefaultRouter()
router.register("", ServiceViewSet, basename="service")

urlpatterns = router.urls
