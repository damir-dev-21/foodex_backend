from django.contrib import admin
from .models import User,Item,Order,OrderItem


class CartInlineAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(User)
class Users(admin.ModelAdmin):
    fieldsets = (
        ('Информация о пользователе',{
            'fields':('name','email','password','latitude','longitude','cart_number','is_superuser')
        }),
    )
    list_display = ('id','name','is_superuser')
    inlines = [CartInlineAdmin]


@admin.register(Item)
class Items(admin.ModelAdmin):
    list_display = ("id","name","photo","price","category_name","restaurant_name","restaurant_logo","restaurant_category","restaurant_delivery","restaurant_delivery_price","created_at","updated_at")


@admin.register(Order)
class Orders(admin.ModelAdmin):
    list_display = ("id","buyer","purchase_time","phone_number","success")
    inlines = [CartInlineAdmin]