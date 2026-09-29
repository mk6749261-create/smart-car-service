from rest_framework.routers import DefaultRouter

from .views import MaintenanceRecordViewSet, MaintenanceRequestViewSet

app_name = "maintenance"

router = DefaultRouter()
router.register("requests", MaintenanceRequestViewSet, basename="maintenance-request")
router.register("records", MaintenanceRecordViewSet, basename="maintenance-record")

urlpatterns = router.urls
