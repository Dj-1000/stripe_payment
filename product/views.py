from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from utils.exceptions.custom_exceptions import ValidationError
from .serializers import ProductSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import Product

class ProductView(APIView):
    def post(self,request):
        serl = ProductSerializer(data = request.data)
        if serl.is_valid():
            resp = {
                'status' : status.HTTP_201_CREATED,
                'resultMessage' : "Product created successfully",
                'result' : serl.data
            }
        else:
            resp = {
                'status' : status.HTTP_400_BAD_REQUEST,
                'errorMessage' : "Invalid product create request",
                'error' : serl.errors
            }
        
        return Response(resp, status=status.HTTP_200_OK)

    def get(self,request,pk=None):
        prod = Product.objects.filetr(id = pk).first()
        serl = ProductSerializer(prod)
        if serl.is_valid():
            resp = {
                'status' : status.HTTP_200_OK,
                'result' : serl.data
            }
        else:
            raise ValidationError("Product does not exist")
        
        return Response(resp, status=status.HTTP_200_OK)

    def put(self,request,pk = None):
        prod = Product.objects.filter(id = pk).first()
        if not prod:
            raise ValidationError("Product does not exist")
        serl = ProductSerializer(prod,data = request.data)
        if serl.is_valid():
            resp = {
                'status' : status.HTTP_201_CREATED,
                'resultMessage' : "Product updated successfully",
                'result' : serl.data
            }
        else:
            resp = {
                'status' : status.HTTP_400_BAD_REQUEST,
                'errorMessage' : "Invalid product update request",
                'error' : serl.errors
            }
        return Response(resp,status=status.HTTP_200_OK)
    
    def delete(self,request,pk=None):
        prod = ProductSerializer.objects.filter(id = pk).first()
        if prod:
            prod.delete()
            resp = {
                'status' : status.HTTP_204_NO_CONTENT,
                'resultMessage' : "Product deleted successfully"
            }
        else:
            raise ValidationError("Product does not exist")
        
        return Response(resp, status=status.HTTP_200_OK)

class ListProductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "result": serializer.data
        },status=status.HTTP_200_OK)
        
