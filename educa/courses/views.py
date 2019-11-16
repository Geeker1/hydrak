from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic.base import TemplateResponseMixin,View
from django.views.generic import ListView,CreateView,UpdateView,DetailView,DeleteView
# Create your views here.
from .models import Course, Module, Content,Subject
from braces.views import LoginRequiredMixin,PermissionRequiredMixin,CsrfExemptMixin,JsonRequestResponseMixin
from django.core.urlresolvers import reverse_lazy
from .forms import ModuleFormSet
from django.apps import apps
from django.forms.models import modelform_factory
from django.db.models import Count
from students.forms import CourseEnrollForm
from django.contrib.auth.models import User
from cart.forms import CartAddProductForm

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class OwnerMixin(object):
    '''
    Used in view
    Interacts with models that have the owner attribute '''
    def get_queryset(self): #to be able to filter objects based on the current user
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)




class OwnerEditMixin(object):
    '''
    This code has the form_valid function that checks if form is valid by using the owner attribute
    It is extended in views where form is needed like updating a view or creating and deleting views
    anything that haas to do with a form
    '''
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)

class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    '''
    This specifies the model so the attribute can extend the filtering based on the model being specified'''
    model = Course


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    '''
    This code specifies the field to be displayed when you want to create,update delete the form
    It specifies the url to move to after the form_valid has been taken care of
    template name speciies the template it extends on all views'''
    fields = ['subject','title','image','slug','overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/form.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class ManageCourseListView(PermissionRequiredMixin, OwnerCourseMixin, ListView):
    permission_required = 'courses.add_course'
    '''
    This justs displays the number of courses but filters it based on the owner that creates it'''
    template_name = 'courses/list.html'
    paginate_by = 4

    def get_queryset(self, **kwargs):
        qs = self.model.objects.all()
        print([q.image for q in qs])
        return super().get_queryset(**kwargs)






class CourseDeleteView(PermissionRequiredMixin, OwnerCourseEditMixin, DeleteView):
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/delete.html'
    permission_required = 'courses.delete_course'

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})

class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/content.html'


    def get_model(self, model_name):
        if model_name in ['text','video','image','file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
        '''
        Checks for if the given model name is one of the four content models:
        text,video,image or file, we use appsmodule to obtain actual class for given model name
        if the given model name is not one of the valid ones, we return None'''

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
            'order',
            'created',
            'updated'])
        return Form(*args, **kwargs)
        '''
        building a dynamic modelform_factory function of the form's framework
        since we are going to build a form from text and video,image and file models
         we use exclude parameter to specify common fields to exclude from form
         and let all other attributes be included automatically. By doing this
          we dont have to know which fields to include depending on model. '''

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
            id=module_id,
            course__owner=request.user)

        self.model = self.get_model(model_name)

        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        '''
        It receives the following url patterns and store corresponding module,model and content object as
         class attributes
         module_id = id for module that the content is/will be associated with.
         model_name = The model name of the content to create/update
         id = the id of the object that is being updated Its None to create new objects
         '''
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form':form,'object': self.obj})
        '''
        Executed on GET request. The model form is built for the instance being updated
        otherwise we pass no instance to create a new object since self.obj is None
        '''

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
            instance=self.obj,
            data=request.POST,
            files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                #new content
                Content.objects.create(module=self.module,
                    item=obj)
            return redirect('module_content_list', self.module.id)
        '''
        Executed when POST request is being received We build model form passing  any submitted data and files
        then we validate if form is valid we create a new object and assign request.user
        as its owner before saving it to database check for id parameter. If no id is provided,
        we know the user is creating a new object instead of updating an existing one. if it is a new
        object we create a "Content" object for given module and associate new content to it'''

        return self.render_to_response({'form':form, 'object':self.obj})

class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
        id=id,
        module__course__owner = request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
            id=module_id,
            course__owner=request.user)

        return self.render_to_response({'module': module})
class ModuleOrderView(CsrfExemptMixin,JsonRequestResponseMixin, View):
    def post(self,request):
        for  id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)

        return  self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        paginator = Paginator(courses, 6)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)


        return self.render_to_response({
            'subjects':subjects,
            'courses':courses,
            'subject':subject,
            'contacts':contacts
            })

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        course = self.get_object()
        context['enroll_form'] = CourseEnrollForm(
            initial={'course':self.object})
        context['cart_product_form'] = CartAddProductForm(
            initial={'course':self.object})
        context['modules'] = course.modules.all()
        return context
    '''
    get_context_data includes
    the enrollment form in the context for rendering the templates
    '''

#@cache_page(CACHE_TTL)
def home(request):
    subjects = Subject.objects.annotate(total_courses=Count('courses'))
    trending = Course.objects.all()[:6]
    is_instructor = request.user.groups.filter(name='Instructors').exists()
    return render(request, 'home.html', {
        'subjects':subjects,
        'trending':trending,
        'is_instructor':is_instructor
        })