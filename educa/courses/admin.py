from django.contrib import admin

from .models import Subject,Course,Module


@admin.register(Subject)
class SubjectModelAdmin(admin.ModelAdmin):
	list_display = ['title','slug']
	prepopulated_fields = {'slug':('title',)}


class ModuleInline(admin.StackedInline):
	model = Module
		
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ['title','slug','created']
	list_filter = ['created','subject']
	search_fields = ['title','overview']
	prepopulated_fields = {'slug':('title',)}

	inlines = [ModuleInline]