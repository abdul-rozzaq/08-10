from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FoodTypeViewSet, FoodViewSet, RegisterAPIView, send_email

app_name = 'project'

router = DefaultRouter()
router.register("food", FoodViewSet)
router.register("food-type", FoodTypeViewSet)
router.register("comment", CommentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterAPIView.as_view()),
    path("send-email/", send_email),
]
