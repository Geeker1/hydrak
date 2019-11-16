from django.shortcuts import render
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic import DetailView,ListView
from django.contrib.auth import authenticate, login
from .forms import StudentForm, CourseEnrollForm
from courses.models import Course, Video
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = StudentForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        result = super(StudentRegistrationView, self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd['username'], email=cd['email'],
            phone=cd['phone'],
            password=cd['password1'])
        login(self.request, user)
        return result


    def get_success_url(self):
        return reverse_lazy('home')

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    paginate_by = 6

    def get_queryset(self):
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView,
         self).get_context_data(**kwargs)
        #get the course object
        course = self.get_object()
        ct = ContentType.objects.get_for_model(Video)
        context['moduleContent'] = []
        if 'module_id' in self.kwargs:
            #get the current module
            context['module'] = course.modules.get(
                id=self.kwargs['module_id'])
            context['moduleContent'] = course.modules.get(
                id=self.kwargs['module_id']).contents.filter(content_type=ct)
        else:
            #get first module
            allCourses = course.modules.all()
            if (allCourses.__len__() > 0):
                context['module'] = allCourses[0]
                context['moduleContent'] = allCourses[0].contents.filter(content_type=ct)
            else:
                context['code'] = 'No modules found in this course'
        coder = context['moduleContent']
        paginator = Paginator(coder, 1)
        page = self.request.GET.get('page')
        try:
            context['contacts'] = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            context['contacts'] = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            context['contacts'] = paginator.page(paginator.num_pages)
        return context

