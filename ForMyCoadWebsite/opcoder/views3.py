from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer
from django.contrib.auth.models import User

@api_view(['GET'])
def get_account_data(request):
    user = User.objects.first()
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
