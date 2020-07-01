from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin ,RetrieveModelMixin,CreateModelMixin,UpdateModelMixin,DestroyModelMixin

from rest_framework.views import APIView

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet

from api.models import Book
from utils.response import APIResponse
from .serializers import BookModelSerializerV2

class BookAPIView(APIView):
    def get(self,request,*args,**kwargs):
        books = Book.objects.all()
        data = BookModelSerializerV2(books,many=True).data

        return APIResponse(status.HTTP_200_OK,results=data)

class BookGenericAPIView(GenericAPIView,
                         ListModelMixin,
                         RetrieveModelMixin,
                         CreateModelMixin,
                         UpdateModelMixin,
                         DestroyModelMixin):

    queryset = Book.objects.all()
    serializer_class = BookModelSerializerV2 #调用你需要的序列化器
    lookup_field = "id"

    # def get(self, request, *args, **kwargs):
    #     books = Book.objects.all()
    #     data = BookModelSerializerV2(books, many=True).data
    #
    #     return APIResponse(status.HTTP_200_OK, results=data)

    #查询全部
    # def get(self, request, *args, **kwargs):
    #     # books = Book.objects.all()
    #     books = self.get_queryset()
    #     # data = BookModelSerializerV2(books, many=True).data
    #     data = self.get_serializer(books,many=True).data
    #
    #     return APIResponse(status.HTTP_200_OK, results=data)

    #查询单个
    # def get(self, request, *args, **kwargs):
    #     # # id = kwargs.get("id")
    #     # # book = Book.objects.get(pk=id,is_delete = False)
    #     # # book = Book.objects.filter(pk=id,is_delete=False).first()
    #     # book = self.get_object()
    #     # # data = BookModelSerializerV2(book, many=False).data
    #     # data = self.get_serializer(book,many=False).data
    #     #
    #     # return APIResponse(status.HTTP_200_OK, results=data)
    #
    #     return self.list(request, *args, **kwargs)
    #
    # def list(self,request,*args,**kwargs):
    #     # id = kwargs.get("id")
    #     # book = Book.objects.get(pk=id,is_delete = False)
    #     # book = Book.objects.filter(pk=id,is_delete=False).first()
    #     book = self.get_object()
    #     # data = BookModelSerializerV2(book, many=False).data
    #     data = self.get_serializer(book, many=False).data
    #
    #     return APIResponse(status.HTTP_200_OK, results=data)
    #通过ListModelMixin查询所有
    # def get(self,request,*args,**kwargs):
    #     return self.list(request,*args,**kwargs)

    #查询单个和所有
    def get(self,request,*args,**kwargs):
        if "id" in kwargs:
            return self.retrieve(request,*args,**kwargs)
        else:
            return self.list(request, *args, **kwargs)
    #添加单个
    def post(self,request,*args,**kwargs):
        response = self.create(request,*args,**kwargs)
        return APIResponse(results=response.data)

    #单个信息整体修改
    def put(self,request,*args,**kwargs):
        response = self.update(request,*args,**kwargs)
        return APIResponse(results=response.data)

    #单个信息局部修改
    def patch(self,request,*args,**kwargs):
        response = self.partial_update(request,*args,**kwargs)  #只是将内部的partial的参数改为True
        return APIResponse(results=response.data)
    #删除单个
    def delete(self,request,*args,**kwargs):
        self.destroy(request,*args,**kwargs)
        return APIResponse(http_status=status.HTTP_204_NO_CONTENT)

#不能有重复定义的方法，因此引用时需要注意
class BookListAPIView(generics.RetrieveAPIView,generics.ListCreateAPIView):
    queryset = Book.objects.filter(is_delete=False)
    serializer_class = BookModelSerializerV2
    lookup_field = "id"


#ModelViewSet继承了GenericViewSet和Mixin
class BookGenericViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.filter(is_delete=False)
    serializer_class = BookModelSerializerV2
    lookup_field = "id"

    def login(self,request,*args,**kwargs):
        request_data = request.data
        book_names = Book.objects.all().values("book_name")
        for bookname in book_names:
            if bookname.get("book_name") == request_data.get("book_name"):
                return APIResponse(data_status=200, data_message="登陆成功!")
            else:
                return APIResponse(data_status=400, data_message="登陆失败!")

    def register(self,request,*args,**kwargs):
        request_data = request.data
        book_names = Book.objects.all().values("book_name")
        for bookname in book_names:
            if bookname.get("book_name") == request_data.get("book_name"):
                return APIResponse(data_status=400, data_message="注册失败")
        BookGenericAPIView.post(self, request, *args, **kwargs)
        return APIResponse(data_status=200, data_message="注册成功")