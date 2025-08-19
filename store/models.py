from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from django.contrib.auth.models import User

# Category Model (Hierarchical)
class Category(MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    objects: models.Manager = TreeManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self) -> str:
        return str(self.name)

#  Product Model:  
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = TreeForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    objects: models.Manager = models.Manager()

    def __str__(self) -> str:
        return str(self.name)

# Order Model:
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    objects: models.Manager = models.Manager()

    def __str__(self) -> str:
        return f"Order {self.pk} by {self.customer}"

        