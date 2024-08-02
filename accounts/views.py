from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from utils.exceptions.custom_exceptions import ValidationError
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import AppUser

class UserView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serl = UserSerializer(data = request.data)
        if serl.is_valid():
            resp = {
                'status' : status.HTTP_201_CREATED,
                'resultMessage' : "App user created successfully",
                'result' : serl.data
            }
        else:
            resp = {
                'status' : status.HTTP_400_BAD_REQUEST,
                'errorMessage' : "Invalid user create request",
                'error' : serl.errors
            }
        
        return Response(resp, status=status.HTTP_200_OK)

    def get(self,request,pk=None):
        user = AppUser.objects.filter(id = pk).first()
        serl = UserSerializer(user,many=False)
        resp = {
            'status' : status.HTTP_200_OK,
            'result' : serl.data
        }
        return Response(resp, status=status.HTTP_200_OK)

    def put(self,request,pk=None):
        user = AppUser.objects.filter(id = pk).first()
        if not user:
            raise ValidationError("User does not exist")
        serl = UserSerializer(user,data = request.data)
        if serl.is_valid():
            resp = {
                'status' : status.HTTP_201_CREATED,
                'resultMessage' : "App user created successfully",
                'result' : serl.data
            }
        else:
            resp = {
                'status' : status.HTTP_400_BAD_REQUEST,
                'errorMessage' : "Invalid user update request",
                'error' : serl.errors
            }
        return Response(resp, status=status.HTTP_200_OK)
    
    def delete(self,request):
        user_id = request.user.id
        user = AppUser.objects.filter(id = user_id).first()
        if user:
            user.delete()
            resp = {
                'status' : status.HTTP_204_NO_CONTENT,
                'resultMessage' : "App user deleted successfully"
            }
        else:
            raise ValidationError("User does not exist")
        
        return Response(resp, status=status.HTTP_200_OK)

class ListUser(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = AppUser.objects.all()
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "result": serializer.data
        },status=status.HTTP_200_OK)
