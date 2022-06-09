from .serializers import UserSerializer, FoodSerializer, OrderSerializer, OrderItemSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User,Item,Order,ItemEncoder,OrderItem
from django.forms.models import model_to_dict
import jwt, datetime
import json



class RegisterUserView(APIView):

    def post(self,request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        responce = Response()
        responce.data = {
            'message':'success',
            'data':serializer.data
        }
        return responce


class LoginView(APIView):

    def post(self, request):

        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload ={
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        serializer = UserSerializer(user)
        responce = Response()

        responce.set_cookie(key='jwt',value=token, httponly=True)

        responce.headers = {
            'jwt':token,
        }

        responce.data = {
            'message':'success',
            'jwt':token,
            'user':serializer.data
        }

        return responce


class LogoutView(APIView):

    def post(self, request):
        responce = Response()
        responce.delete_cookie('jwt')
        responce.data = {
            'message': 'success'
        }
        return responce

class NewItems(APIView):

    def get(self,request):

        items = Item.objects.all()

        list_of_news = []

        for i in items:
            date = str(i.created_at).split(' ')[0].split('-')
            date_of_created = datetime.date(int(date[0]),int(date[1]),int(date[2]))
            current_date = datetime.date.today()
            t = date_of_created - current_date


            if t.days >= -3 and t.days <= 0:
                item = model_to_dict(i)
                list_of_news.append(item)

        responce = Response()
        responce.data = json.dumps(list_of_news,ensure_ascii=False)
        responce.content_type = 'application/json'
        return Response(list_of_news)


class UserOrders(APIView):

    def post(self,request):
        orders = OrderItem.objects.all()
        user = User.objects.filter(id=request.data['id']).first()
        list_of_orders = []
        for i in orders:
            if(i.user.id == user.id):
                list_of_orders.append(model_to_dict(i))

        responce = Response()
        responce.data = list_of_orders
        return responce


class FoodListView(APIView):

    def get(self, request):
        # token = request.COOKIES.get('jwt')
        #
        # if not token:
        #     raise AuthenticationFailed('Unauth')
        #
        # try:
        #     payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        # except jwt.ExpiredSignatureError:
        #     raise AuthenticationFailed('Unauth')

        #user = User.objects.filter(id=payload['id']).first()

        # if user:
        queryset = Item.objects.all()
        serializer = FoodSerializer(queryset,many=True)
        responce = Response()
        # responce.headers = {
        #     'jwt': token,
        # }
        responce.data = serializer.data
        return responce
        # else:
        #     content = {'Ошибка авторизации': 'вы не авторизованы'}
        #     return Response(content,status=status.HTTP_401_UNAUTHORIZED)


class FoodDetailView(generics.RetrieveAPIView):

    queryset = Item.objects.all()
    serializer_class = FoodSerializer
    lookup_field = 'id'

class OrderDetailView(generics.RetrieveAPIView):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'


class OrderListView(APIView):

    def get(self,request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Неавторизованный пользователь')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauth')

        user = User.objects.filter(id=payload['id']).first()

        if user.is_superuser:
            queryset = Order.objects.all()
            serializer = OrderSerializer(queryset, many=True)
            responce = Response()
            responce.headers = {
                'jwt': token,
            }
            responce.data = serializer.data
            return responce
        else:
            content = {'Ошибка авторизации': 'вы не авторизованы как админ'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)


class OrderCreateView(APIView):

    def get(self,request):
        return Response({"Get method is":'true'})

    def post(self, request):

        user = User.objects.filter(id=int(request.data['buyer'])).first()

        user_id = user.id

        products = request.data['cart']

        total = 0

        for i in products:
            product = Item.objects.filter(id=i['product']).first()
            total = total + (int("".join(product.price.split(','))) * i['quantity'])

        new_item_order = {
            "buyer":user_id,
            "total": total,
            "phone_number":request.data['phone_number'],
            "success":request.data['success']
        }

        serializer = OrderSerializer(data=new_item_order)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        order_id = serializer.data['id']

        for i in products:

            product = Item.objects.filter(id=i['product']).first()

            new_item = {
                "order":order_id,
                "user" : user_id,
                "product" : i['product'],
                "amount" : product.price,
                "quantity" : i['quantity']
            }

            order_item_ser = OrderItemSerializer(data=new_item)
            order_item_ser.is_valid(raise_exception=True)
            order_item_ser.save()

        return Response(serializer.data)


class OrderUpdateView(APIView):

    def put(self,request,id):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Вы не авторизованы')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Вы не авторизованы")

        user = User.objects.filter(id=payload['id']).first()

        if user.is_superuser:
            order = Order.objects.get(id=id)
            status =  not order.success

            new_item = {
                "id":id,
                "buyer":order.buyer.id,
                "phone_number":order.phone_number,
                "total":order.total,
                "purchase_time":order.purchase_time,
                "success":status
            }

            orderSerializer = OrderSerializer(order,data=new_item)
            orderSerializer.is_valid(raise_exception=True)
            orderSerializer.save()
            return Response({"Объект обновлен": f"Статус заказа c id {id} изменен"})
        else:
            return Response({"Ошибка авторизации": "Вы не авторизованы как админ"})


class OrderDeleteView(APIView):

    def delete(self,request,id):

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Вы не авторизованы')

        try:
            payload = jwt.decode(token,'secret',algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Вы не авторизованы")

        user = User.objects.filter(id=payload['id']).first()

        if user.is_superuser:
            order = Order.objects.get(id=id)
            order.delete()
            return Response({"Объект удален": f"Заказ c id {id} удален"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"Ошибка авторизации":"Вы не авторизованы как админ"})