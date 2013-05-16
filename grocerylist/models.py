from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

class Aisle(models.Model):
	name = models.CharField(max_length=100)
	store = models.ForeignKey(Store)
	sort = models.IntegerField()
	owner = models.ForeignKey(User)

	class Meta:
		permissions = (
            ("change_own_aisle", "Can edit own aisles"),
        )


	def __unicode__(self):
		return self.name + ' @ ' + self.store.name

class Product(models.Model):
	name = models.CharField(max_length=100)
	aisles = models.ManyToManyField(Aisle)
	owner = models.ForeignKey(User)

	class Meta:
		permissions = (
            ("change_own_product", "Can edit own products"),
        )

	def __unicode__(self):
		return self.name

class Glist(models.Model):
	name = models.CharField(max_length=100)
	products = models.ManyToManyField(Product, through='Item')
	store = models.ForeignKey(Store)
	owner = models.ForeignKey(User)
	def __unicode__(self):
		return self.name

	class Meta:
		permissions = (
            ("change_own_glist", "Can edit own glists"),
        )

class Item(models.Model):
	product = models.ForeignKey(Product)
	glist = models.ForeignKey(Glist)
	got_it = models.BooleanField()

	def active_aisle(self):
		#returns the item's corresponding aisle for this list's store
		aisle = self.product.aisles.filter(store_id = self.glist.store_id)
		#should throw an error if there's more than one
		return aisle[0]

	def __unicode__(self):
		return self.product.name





