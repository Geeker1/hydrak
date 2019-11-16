from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
# Create your models here.


class Subject(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True)

	class Meta:
		ordering = ('title',)


	def __str__(self):
		return self.title


class Course(models.Model):
	owner = models.ForeignKey(User, related_name='courses_created')
	subject = models.ForeignKey(Subject, related_name='courses')
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True)
	price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	overview = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	students = models.ManyToManyField(User, related_name='courses_joined',
		blank=True)
	image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True)


	class Meta:
		ordering = ('-created',)

	def __str__(self):
		return self.title




class Module(models.Model):
	course = models.ForeignKey(Course,related_name='modules')
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	order = OrderField(blank=True, for_fields=['course'])

	class Meta:
		ordering = ['order']

	def __str__(self):
		return '{}. {}'.format(self.order, self.title)



class Content(models.Model):
	module = models.ForeignKey(Module,related_name='contents')#This relates the content to the module since the module has different content
	content_type = models.ForeignKey(ContentType,limit_choices_to = {
		'model__in':('text',
			'video','image','file')
		})
	object_id = models.PositiveIntegerField()
	item = GenericForeignKey('content_type','object_id')#allows you to retrieve or set the object directly,its functionality is based on the objects it stores
	order = OrderField(blank=True, for_fields=['module'])

	class Meta:
		ordering = ['order']


class ItemBase(models.Model):
	owner = models.ForeignKey(User,related_name='%(class)s_related')
	title = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.title

	def render(self):
		return render_to_string('courses/content/{}.html'.format(
			self._meta.model_name), {'item': self})


class Text(ItemBase):
	content = models.TextField()

class File(ItemBase):
	file = models.FileField(upload_to='files')

class Image(ItemBase):
	file = models.FileField(upload_to='images')

class Video(ItemBase):
	file = models.URLField()