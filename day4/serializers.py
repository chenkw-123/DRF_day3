from rest_framework import serializers, exceptions

from api.models import Book


class BookListSerializer(serializers.ListSerializer):
    # 使用此序列化器完成修改多个对象
    def update(self, instance, validated_data):
        # print(type(self))  # 当前调用序列化器类
        # print(instance)  # 要修改的对象
        # print(validated_data)   # 要修改的数据
        # print(type(self.child))

        for index, obj in enumerate(instance):
            # 每遍历一次 就修改一个对象的数据
            self.child.update(obj, validated_data[index])

        return instance

class BookModelSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = Book
        # fields应该填写哪些字段  应该填写序列化与反序列化字段的并集
        fields = ("book_name", "price", "publish", "authors", "pic")

        #未修改多个对象，使用ListSerializer
        list_serializer_class =  BookListSerializer
        # 添加DRF所提供的校验规则
        # 通过此参数指定哪些字段是参与序列化的  哪些字段是参与反序列化的
        extra_kwargs = {
            "book_name": {
                "required": True,  # 设置为必填字段
                "min_length": 2,  # 最小长度
                "error_messages": {
                    "required": "图书名不能为空",
                    "min_length": "长度太短"
                }
            },
            # 指定此字段只参与反序列化
            "publish": {
                "write_only": True
            },
            "authors": {
                "write_only": True
            },
            # 指定某个字段只参与序列化
            "pic": {
                "read_only": True
            }
        }

    def validate_book_name(self, value):
        # 自定义用户名校验规则
        if "1" in value:
            raise exceptions.ValidationError("图书名含有敏感字")
        request = self.context.get("request")
        print(request.method)
        return value

    # 全局校验钩子  可以通过attrs获取到前台发送的所有的参数
    def validate(self, attrs):

        price = attrs.get("price", 0)
        # 没有获取到 price  所以是 NoneType
        if price > 90:
            raise exceptions.ValidationError("超过设定的最高价钱~")

        return attrs



