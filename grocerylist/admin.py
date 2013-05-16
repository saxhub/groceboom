from django.contrib import admin
from grocerylist.models import Store, Aisle, Product, Glist, Item

admin.site.register(Glist)
admin.site.register(Store)
admin.site.register(Aisle)
admin.site.register(Product)
admin.site.register(Item)
