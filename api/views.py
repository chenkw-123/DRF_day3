from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.models import Book
from utils.response import APIResponse
from .serializers import BookModelSerializer, BookDeModelSerializer, BookModelSerializerV2


class BookAPIView(APIView):

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("id")
        if book_id:

            book_obj = Book.objects.get(pk=book_id)
            book_ser = BookModelSerializer(book_obj).data
            return Response({
                "status": status.HTTP_200_OK,
                "message": "查询单个图书成功",
                "results": book_ser
            })

        else:
            book_list = Book.objects.all()
            book_list_ser = BookModelSerializer(book_list, many=True).data
            return Response({
                "status": status.HTTP_200_OK,
                "message": "查询所有图书成功",
                "results": book_list_ser
            })

    def post(self, request, *args, **kwargs):
        """
        完成增加单个对象
        """
        request_data = request.data

        # 将前端发送过来的数据交给反序列化器进行校验
        book_ser = BookDeModelSerializer(data=request_data)

        # 校验数据是否合法 raise_exception：一旦校验失败 立即抛出异常
        book_ser.is_valid(raise_exception=True)
        book_obj = book_ser.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "添加图书成功",
            "result": BookModelSerializer(book_obj).data
        })


class BookAPIViewV2(APIView):

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("id")
        if book_id:

            book_obj = Book.objects.filter(pk=book_id, is_delete=False).first()
            book_ser = BookModelSerializerV2(book_obj).data
            # return Response({
            #     "status": status.HTTP_200_OK,
            #     "message": "查询单个图书成功",
            #     "results": book_ser
            # })
            return APIResponse(status.HTTP_200_OK,"成功啦",results=book_ser)

        else:
            book_list = Book.objects.filter(is_delete=False)
            book_list_ser = BookModelSerializerV2(book_list, many=True).data
            # return Response({
            #     "status": status.HTTP_200_OK,
            #     "message": "查询所有图书成功",
            #     "results": book_list_ser
            # })
            return APIResponse(status.HTTP_200_OK,"查询全部成功",results=book_list_ser)


    def post(self, request, *args, **kwargs):
        request_data = request.data
        if isinstance(request_data, dict):  # 代表增加的是单个图书
            # 将前端发送过来的数据交给反序列化器进行校验
            many = False
        elif isinstance(request_data, list):  # 代表添加多个图书
            many = True
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "请求参数格式有误",
            })

        book_ser = BookModelSerializerV2(data=request_data, many=many ,context={"request":request})
        # 校验数据是否合法 raise_exception：一旦校验失败 立即抛出异常
        book_ser.is_valid(raise_exception=True)
        book_obj = book_ser.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "添加图书成功",
            # 当群增多个时，无法序列化多个对象到前台  所以报错
            "result": BookModelSerializerV2(book_obj, many=many).data
        })

    def delete(self, request, *args, **kwargs):
        book_id = kwargs.get("id")
        if book_id:
            # 删除单个  也作为删除多个
            ids = [book_id]
        else:
            # 删除多个
            ids = request.data.get("ids")

        # 判断传递过来的图书的id是否在数据库  且还未删除
        response = Book.objects.filter(pk__in=ids, is_delete=False).update(is_delete=True)
        if response:
            return Response({
                "status": status.HTTP_200_OK,
                "message": "删除成功"
            })

        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "删除失败或图书不存在"
        })

    def put(self, request, *args, **kwargs):
        # 修改的参数
        request_data = request.data
        # 要修改的图书的id
        book_id = kwargs.get("id")

        try:
            book_obj = Book.objects.get(pk=book_id)
        except:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "图书不存在"
            })

        # 前端发送了修改的参数request_data 数据更新需要校验
        # 更新 的时候将参数赋值data  方便钩子函数校验
        book_ser = BookModelSerializerV2(data=request_data, instance=book_obj, partial=False)
        book_ser.is_valid(raise_exception=True)

        # 经过序列化器规则校验 局部全局钩子校验通过后则调用 update()方法完成更新
        book_ser.save()

        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "更新成功",
            "results": BookModelSerializerV2(book_obj).data
        })

    # def patch(self, request, *args, **kwargs):
    #
    #     request_data = request.data
    #     book_id = kwargs.get("id")
    #
    #     try:
    #         book_obj = Book.objects.get(pk=book_id)
    #     except:
    #         return Response({
    #             "status": status.HTTP_400_BAD_REQUEST,
    #             "message": "图书不存在"
    #         })
    #     book_ser = BookModelSerializerV2(data=request_data, instance=book_obj, partial=True)
    #     book_ser.is_valid(raise_exception=True)
    #
    #     book_ser.save()
    #
    #     return Response({
    #         "status": status.HTTP_400_BAD_REQUEST,
    #         "message": "更新成功",
    #         "results": BookModelSerializerV2(book_obj).data
    #     })


    def patch(self,request,*args,**kwargs):
        request_data = request.data
        book_id = kwargs.get("id")
        #当id存在时，且传递的参数为字典，则代表修改单个
        if book_id and isinstance(request_data, dict):
            book_ids = [book_id, ]
            request_data = [request_data]
            #id不存在，传递参数为裂变，修改多个
        elif not book_id and isinstance(request_data, list):
            book_ids = []
            # 将要修改的图书的id取出放进 book_ids中
            for dic in request_data:
                pk = dic.pop("pk", None)
                if pk:
                    book_ids.append(pk)
                else:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "PK不存在",
                    })
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "数据格式错误",
            })
        # print(request_data)
        # print(book_id)

        # books = []#要修改的图书对象
        # new_updata_data = [] #要修改的参数
        # #当图书不存在时，不修改，继续执行，如果存在，则查询出来修改
        # #不能再循环中对列表长度做改变
        # for index, pk in enumerate(book_ids):
        #     #index是book_ids的每一个元素的下标
        #     try:
        #         book_obj = Book.objects.get(pk=pk),
        #         books.append(book_obj)
        #         #把修改后的信息按照下标放入要修改的参数列表中
        #         new_updata_data.append(request_data[index])
        #         # print(request_data[index])
        #     except:
        #         #当报错时什么都不执行，不修改不存在的id的数据，不能一处
        #         continue

        book_list = []  # 所有要修改的图书对象
        new_data = []  # 所有要修改的参数
        #  禁止在循环中对列表的长度做改变
        for index, pk in enumerate(book_ids):
            try:
                book_obj = Book.objects.get(pk=pk)
                book_list.append(book_obj)
                new_data.append(request_data[index])
                # print(request_data[index])
            except:
                # 如果图书对象不存在  则将id与对应数据都移除
                # index = book_ids.index(pk)
                # request_data.pop(index)
                continue

        # book = Book.objects.get(pk="id")
        book_msg = BookModelSerializerV2(data=request_data,instance=book_list,partial=True,many=True)
        book_msg.is_valid(raise_exception=True)
        book_msg.save()

        return Response({
            "status":status.HTTP_200_OK,
            "message":"数据修改成功"
        })


