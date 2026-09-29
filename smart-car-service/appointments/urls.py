from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, ServiceSlotViewSet

app_name = "appointments"

router = DefaultRouter()
router.register("slots", ServiceSlotViewSet, basename="service-slot")
router.register("", AppointmentViewSet, basename="appointment")

urlpatterns = router.urls
