from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"people", views.PeopleViewSet)
router.register(r"users", views.UsersViewSet)
router.register(r"roles", views.RolesViewSet)
router.register(r"userroles", views.UserRolesViewSet)
router.register(r"establishments", views.EstablishmentsViewSet)
router.register(r"slots", views.SlotsViewSet)
router.register(r"slotstatus", views.SlotStatusViewSet)
router.register(r"apikeys", views.ApiKeysViewSet)
router.register(r"cameras", views.CamerasViewSet)
router.register(r"refreshtokens", views.RefreshTokensViewSet)
router.register(r"clients", views.ClientsViewSet)
router.register(r"clientmembers", views.ClientMembersViewSet)
router.register(r"storetypes", views.StoreTypesViewSet)
router.register(r"lots", views.LotsViewSet)
router.register(r"slottypes", views.SlotTypesViewSet)
router.register(r"vehicletypes", views.VehicleTypesViewSet)
router.register(r"slotstatushistory", views.SlotStatusHistoryViewSet)
router.register(r"cameraheartbeats", views.CameraHeartbeatsViewSet)
router.register(r"slotstatusevents", views.SlotStatusEventsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
