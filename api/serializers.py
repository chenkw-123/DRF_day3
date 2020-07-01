from rest_framework import serializers, exceptions

from api.models import Book, Press


class PressModelSerializer(serializers.ModelSerializer):
    #出版社的序列化器

    class Meta :
    #    指定序列化的model
        model = Press
        #指定要序列化的字段，即在前端显示出来的（必须是model中所拥有的）

        fields = ("press_name", "address", "pic")


class BookModelSerializer(serializers.ModelSerializer):
    # 为序列化器自定以字段 (不推荐)
    # abc = serializers.SerializerMethodField()
    #
    # def abc(self, obj):
    #     return "abc"

    #序列化器的嵌套，使用出版社的序列化器
    # 可以在序列化器中嵌套另一个序列化器来查询外键的所有信息，需要与Book中外键名保持一致
    publish = PressModelSerializer()

    class Meta:
        # 指定当前序列化器要序列化的模型
        model = Book
        # 指定序列化模型的字段，显示在前端
        # fields = ("book_name", "price", "pic", "publish_name", "press_address", "author_list", "publish")

        #嵌套序列化器后，可以直接将嵌套的序列化器的内容直接指定
        fields = ("book_name", "price", "pic", "publish")

        # 查询所有信息
        # fields = "__all__"

        # 指定这些字段不显示
        # exclude = ("is_delete", "create_time", "status")

        # 指定查询深度  关联对象的查询  可以查询出有外键关系的信息
        #查询出外键的所有信息
        # depth = 1


class BookDeModelSerializer(serializers.ModelSerializer):
    #反序列器，添加数据 即POST请求时使用

    class Meta:
        model = Book
        fields = ("book_name", "price", "publish", "authors")

        # 添加DRF所提供的校验规
        extra_kwargs = {
            "book_name": {
                "required": True,  # 设置为必填字段
                "min_length": 3,  # 最小长度
                "error_messages": {
                    "required": "图书名是必填的",
                    "min_length": "长度不够，太短啦~"
                }
            },
            "price": {
                "max_digits": 5,
                "decimal_places": 4,
            }
        }

    def validate_book_name(self, value):
        # 自定义用户名校验规则
        if "1" in value:
            raise exceptions.ValidationError("图书名含有敏感字")
        return value

    # 全局校验钩子  可以通过attrs获取到前台发送的所有的参数
    def validate(self, attrs):
        # print(self, "111222333")
        pwd = attrs.get("password")
        re_pwd = attrs.pop("re_pwd")
        # 自定义规则  两次密码如果不一致  则无法保存
        if pwd != re_pwd:
            raise exceptions.ValidationError("两次密码不一致")

        return attrs


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



