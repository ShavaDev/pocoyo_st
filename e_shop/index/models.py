from tabnanny import verbose

from django.db import models


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=32, verbose_name='Название категории')
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'категорию'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    product_name = models.CharField(max_length=128, verbose_name='Название товара')
    product_des = models.TextField(blank=True, null=True, verbose_name='Описание товара')
    product_count = models.IntegerField(verbose_name='Кол-во товара на складе')
    product_price = models.FloatField(verbose_name='Цена товара')
    product_photo = models.ImageField(upload_to='images', verbose_name='Фото товара')
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория товара')
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'


class Cart(models.Model):
    user_id = models.IntegerField()
    user_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_pr_amount = models.IntegerField()

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
