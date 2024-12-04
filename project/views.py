from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Comment, Food, FoodType
from .permissions import IsCreator
from .serializers import CommentSerializer, EmailMessageSerializer, FoodSerializer, FoodTypeSerializer, RegisterSerializer

User = get_user_model()


class FoodViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    queryset = Food.objects.all()
    permission_classes = [IsAdminUser]
    filterset_fields = ["food_type"]
    search_fields = ["nomi"]


class FoodTypeViewSet(viewsets.ModelViewSet):
    serializer_class = FoodTypeSerializer
    queryset = FoodType.objects.all()
    permission_classes = [IsAdminUser]
    search_fields = ["name"]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCreator]
    search_fields = ["text", "food__nomi", "author__username"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RegisterAPIView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Ro'yhatdan o'tish",
        operation_id="register",
        operation_description="Ro'yxatdan o'tish uchun API",
        request_body=RegisterSerializer,
        tags=["auth"],
    )
    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({"message": "User created successfully", "access_token": access_token, "refresh_token": str(refresh)})


@api_view(["POST"])
@swagger_auto_schema(request_body=EmailMessageSerializer)
@permission_classes([IsAdminUser])
def send_email(request):
    response = {}

    serializer = EmailMessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    title = serializer.validated_data["title"]
    message = serializer.validated_data["message"]

    for user in User.objects.all():
        response[user.email] = bool(
            send_mail(
                title,
                message,
                [settings.EMAIL_HOST_USER],
                [user.email],
                fail_silently=False,
            )
        )

    return Response(response)
