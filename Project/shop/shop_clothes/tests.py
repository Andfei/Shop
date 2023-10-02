import zoneinfo
from _decimal import Decimal
from datetime import timezone

from django.contrib.auth.models import User
from django.test import TestCase

from shop_clothes.models import Product, Payment, OrderItem, Order

class TestDataBase(TestCase):
    fixtures = [
        "shop/shop_clothes/fixtures/data.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='root')
        self.p = Product.objects.all().first()

    def test_user_exists(self):
        users = User.objects.all()
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 1)
        self.assertEqual(user.username, 'root')
        self.assertTrue(user.is_superuser)

    def test_user_check_password(self):
        self.assertTrue(self.user.check_password('123'))

    def test_all_data(self):
        self.assertGreater(Product.objects.all().count(), 0)
        self.assertGreater(Payment.objects.all().count(), 0)
        self.assertGreater(Order.objects.all().count(), 0)
        self.assertGreater(OrderItem.objects.all().count(), 0)

    def find_card_number(self):
        cart_number = Order.objects.filter(user=self.user, status=Order.STATUS_CART).count()
        return cart_number

    def test_function_get_car(self):
        # no carts
        self.assertEqual(self.find_card_number(), 0)
        Order.get_cart(self.user)
        # create carts
        self.assertEqual(self.find_card_number(), 1)
        # Get create cart
        Order.get_cart(self.user)
        self.assertEqual(self.find_card_number(), 1)

    def test_cart_older_7_days(self):
        cart = Order.get_cart(self.user)
        cart.creation_time = timezone.datetime(2000, 1, 1, tzinfo=zoneinfo.ZoneInfo('UTS'))
        cart.save()
        cart = Order.get_cart(self.user)
        self.assertEqual((timezone.now() - cart.creation_time).days, 0)

    def test_recalculate_order_amount_changing_orderitem(self):
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))

        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quintity=2)
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quintity=3)
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(10))

        i.delete()
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(4))

    def test_cart_status_changing_after_applying_make_order(self):
        pass

    def test_method_get_amount_of_unpaid_orders(self):
        pass