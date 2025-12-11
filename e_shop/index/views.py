from django.shortcuts import render, redirect
from . import models
from . import forms
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django import views
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Create your views here.
# работа с тг ботом
bot = telebot.TeleBot('TOKEN')
admin_id = 'ADMIN_ID'

# работа с Google таблицами
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('index/credentials.json', scope)
gs = gspread.authorize(creds)


# Главная страница
def home_page(request):
    # Достаем данные из БД
    categories = models.Category.objects.all()
    products = models.Product.objects.all()
    # Передаем данные на Frontend
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'home.html', context)


# Страница с товарами по категории
def category_page(request, pk):
    # Достаем данные из БД
    category = models.Category.objects.get(id=pk)
    products = models.Product.objects.filter(product_category=category)
    # Передаем данные на Frontend
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'category.html', context)


# Страница определенного товара
def product_page(request, pk):
    # Достаем данные из БД
    product = models.Product.objects.get(id=pk)
    # Передаем данные на Frontend
    context = {'product': product}
    return render(request, 'product.html', context)


# Поиск товара по названию
def search(request):
    if request.method == 'POST':
        # Достаем данные с формы
        search_product = request.POST.get('search_product')
        # Достаем данные из БД
        get_product = models.Product.objects.filter(product_name__iregex=search_product)
        # Передаем данные на фронт
        context = {}
        if get_product:
            context.update(user_pr=search_product, products=get_product)
        else:
            context.update(user_pr=search_product, products='')
        return render(request, 'result.html', context)


# Регистрация (класс представления)
class Register(views.View):
    template_name = 'registration/register.html'

    def get(self, request):
        form = forms.RegForm
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = forms.RegForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password2')

            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
            user.save()
            login(request, user)
        return redirect('/')


# Добавление товара в корзину
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = models.Product.objects.get(id=pk)
        user_count = int(request.POST.get('pr_amount'))
        print(user_count)

        if 1 <= user_count <= product.product_count:
            models.Cart.objects.create(user_id=request.user.id,
                                       user_product=product,
                                       user_pr_amount=user_count).save()
            return redirect('/')
        return redirect(f'/product/{pk}')


# отображение корзины
def cart_page(request):
    # Достаем данные из БД
    user_cart = models.Cart.objects.filter(user_id=request.user.id)
    # Подсчет итоговых стоимостей
    totals = [round(t.user_pr_amount * t.user_product.product_price, 2) for t in user_cart]
    # Передаем данные на Frontend
    context = {
        'cart': user_cart,
        'total': round(sum(totals), 2)
    }

    # Оформление заказа
    if request.method == 'POST':
        text = (f'Новый заказ!\n'
                f'Клиент: {User.objects.get(id=request.user.id).email}\n\n')
        new_totals = []
        for i in user_cart:
            # Подготовка текста для Telegram бота
            product = models.Product.objects.get(id=i.user_product.id)  # Достаем выбранный товар из БД
            user_amount = int(request.POST.get(f'amount_{i.user_product.id}'))  # Достаем кол-во с формы
            product.product_count = product.product_count - user_amount
            product.save(update_fields=['product_count'])
            new_totals.append(round(user_amount * product.product_price, 2))
            text += f'Товар: {i.user_product}\nКол-во: {user_amount}\n\n'

            # Добавление данных в Google таблицы
            table = gs.open('Заказы')
            sheet = table.sheet1
            sheet.append_row([User.objects.get(id=request.user.id).email, i.user_product.product_name, user_amount])

        text += f'Итого: ${round(sum(new_totals), 2)}'
        bot.send_message(admin_id, text)
        user_cart.delete()
        return redirect('/')
    return render(request, 'cart.html', context)


# удаление из корзины
def del_from_cart(request, pk):
    models.Cart.objects.filter(user_product=models.Product.objects.get(id=pk)).delete()
    return redirect('/')


# выход из аккаунта
def logout_view(request):
    logout(request)
    return redirect('/')
