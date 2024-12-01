from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Comment, Food, FoodType
from .permissions import IsCreator
from .serializers import CommentSerializer, FoodSerializer, FoodTypeSerializer, RegisterSerializer


class FoodAPIView(ListCreateAPIView):
    serializer_class = FoodSerializer
    queryset = Food.objects.all()
    permission_classes = [IsAdminUser]
    filterset_fields = ["food_type"]
    search_fields = ["nomi"]


class FoodDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = FoodSerializer
    queryset = Food.objects.all()
    permission_classes = [IsAdminUser]


class FoodTypeAPIView(ListCreateAPIView):
    serializer_class = FoodTypeSerializer
    queryset = FoodType.objects.all()
    permission_classes = [IsAdminUser]
    search_fields = ["name"]


class FoodTypeDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = FoodTypeSerializer
    queryset = FoodType.objects.all()
    permission_classes = [IsAdminUser]


class CommentAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCreator]
    search_fields = ["text", "food__nomi", "author__username"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCreator]


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
