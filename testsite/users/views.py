from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.views import View

from users.forms import UserCreationForm, AuthenticationForm
from users.utils import send_email_for_verify
from django.contrib.auth.tokens import default_token_generator as token_generator

from rest_framework.views import APIView
from .models import Tasks
from .serializers import TasksSerializer, TaskDetailSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .forms import AddTaskForm, TaskForm

class SmartTasksAPIView(APIView):
    def get(self, request):
        tasks = Tasks.objects.all()
        # Проверяем каждую задачу
        # for task in tasks:
        #     # Проверяем, отличается ли дата выполнения задачи от сегодняшней даты менее чем на 3 дня
        #     if -3 < task.day_to_do - timezone.now().date().days < 3:
        #         # Обновляем флаг urgent
        #         task.urgent = True
        #         task.save()
        #     elif task.day_to_do - timezone.now().date().days <= -3:
        #         task.urgent = False
        #         task.importance = False
        #         task.save()
        user = request.user
        tasks = Tasks.objects.filter(username=user.email)
        smart_tasks = tasks.filter(urgent=False, important=True, done=False).order_by('-time_update')
        smart_urgent_tasks = tasks.filter(urgent=True, important=True, done=False).order_by('-time_update')
        other_tasks = tasks.filter(urgent=True, important=False, done=False).order_by('-time_update')
        sorted_tasks = list(smart_tasks) + list(smart_urgent_tasks) + list(other_tasks)
        serializer = TasksSerializer(sorted_tasks, many=True)
        return Response(serializer.data)


class TaskDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskDetailSerializer
    @swagger_auto_schema(responses={200: TaskDetailSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.username != request.user.email:
            return Response({"error": "You don't have permission to access this task."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Task updated successfully', 'data': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.views.generic import ListView, DetailView, UpdateView, CreateView
class TasksHome(ListView):
    model = Tasks
    template_name = 'home.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Tasks.objects.filter(username=user.email, done=False).order_by('-time_update')
        else:
            return Tasks.objects.none()
# def index(request):
#     user = request.user
#     if user.is_authenticated:
#         tasks = Tasks.objects.all().order_by('-time_update')
#         tasks = tasks.filter(username=user.email, done=False)
#     else:
#         tasks = []
#     return render(request, 'home.html', {'tasks': tasks})

class TasksArchive(ListView):
    model = Tasks
    template_name = 'home.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Tasks.objects.filter(username=user.email, done=True).order_by('-time_update')
        else:
            return Tasks.objects.none()
# def archive(request):
#     user = request.user
#     if user.is_authenticated:
#         tasks = Tasks.objects.all().order_by('-time_update')
#         tasks = tasks.filter(username=user.email, done=True)
#     else:
#         tasks = []
#     return render(request, 'home.html', {'tasks': tasks})

class TasksDetail(UpdateView):
    model = Tasks
    template_name = 'task.html'
    form_class = TaskForm
    context_object_name = 'task'
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Tasks.objects.filter(username=user.email)
        else:
            return Tasks.objects.none()
    def get_success_url(self):
        return reverse_lazy('home')


# def show_task(request, task_id):
#     user = request.user
#     if user.is_authenticated:
#         tasks = Tasks.objects.all()
#         tasks = tasks.filter(username=user.email, id=pk)
#     else:
#         tasks = []
#     return render(request, 'task.html', {'tasks': tasks})


# def smart(request):
#     user = request.user
#     if user.is_authenticated:
#         tasks = Tasks.objects.filter(username=user.email)
#         smart_tasks = tasks.filter(urgent=False, important=True, done=False).order_by('-time_update')
#         smart_urgent_tasks = tasks.filter(urgent=True, important=True, done=False).order_by('-time_update')
#         other_tasks = tasks.filter(urgent=True, important=False, done=False).order_by('-time_update')
#         sorted_tasks = list(smart_tasks) + list(smart_urgent_tasks) + list(other_tasks)
#     else:
#         sorted_tasks = []
#     return render(request, 'home.html', {'tasks': sorted_tasks})

class TasksSmart(ListView):
    template_name = 'home.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            tasks = Tasks.objects.filter(username=user.email)
            smart_tasks = tasks.filter(urgent=False, important=True, done=False).order_by('-time_update')
            smart_urgent_tasks = tasks.filter(urgent=True, important=True, done=False).order_by('-time_update')
            other_tasks = tasks.filter(urgent=True, important=False, done=False).order_by('-time_update')
            sorted_tasks = list(smart_tasks) + list(smart_urgent_tasks) + list(other_tasks)
            return sorted_tasks
        else:
            return []

class TasksImportant(ListView):
    template_name = 'home.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            tasks = Tasks.objects.filter(username=user.email, important=True, done=False).order_by('-time_update')
            return tasks
        else:
            return []
class TasksUrgent(ListView):
    template_name = 'home.html'
    context_object_name = 'tasks'
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            tasks = Tasks.objects.filter(username=user.email, urgent=True, done=False).order_by('-time_update')
            return tasks
        else:
            return []

class AddTask(CreateView):
    form_class = AddTaskForm
    template_name = 'add_task.html'
    def form_valid(self, form):
        form.instance.username = self.request.user.email
        return super().form_valid(form)
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)
    def get_success_url(self):
        return reverse_lazy('home')

# def add_task(request):
#     user = request.user
#     if not user.is_authenticated:
#         return redirect('home')
#     if request.method == 'POST':
#         form = AddTaskForm(request.POST)
#         if form.is_valid():
#             form.instance.username = user.email  # Задаем значение username
#             form.save()
#             return redirect('home')
#     else:
#         form = AddTaskForm()
#     return render(request, 'add_task.html', {'form': form})
#

# def add_task(request):
#     user = request.user
#     if not user.is_authenticated:
#         return redirect('home')
#     if request.method == 'POST':
#         form = AddTaskForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             try:
#                 Tasks.objects.create(**form.cleaned_data, username=user.email)
#                 print("ура поббебы ура победа")
#             except:
#                 print("Ошибка добавления поста")
#             return redirect('home')
#     else:
#         form = AddTaskForm()
#     return render(request, 'add_task.html', {'form': form})
#


# def search(request):
#     user = request.user
#     if user.is_authenticated:
#         tasks = Tasks.objects.all().order_by('-time_update')
#         tasks = tasks.filter(username=user.email, done=False)
#     else:
#         tasks = []
#     return render(request, 'home.html', {'tasks': tasks})
from django.urls import reverse_lazy
from django.views.generic import DeleteView

class TaskDeleteView(DeleteView):
    model = Tasks
    success_url = reverse_lazy('home')  # перенаправление после успешного удаления
    template_name = 'task_confirm_delete.html'
class TasksAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Title of the task", type=openapi.TYPE_STRING),
            openapi.Parameter('day_to_do', openapi.IN_QUERY, description="Day to do the task", type=openapi.TYPE_STRING),
            openapi.Parameter('done', openapi.IN_QUERY, description="Whether the task is done or not", type=openapi.TYPE_STRING),
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the task", type=openapi.TYPE_INTEGER),
            openapi.Parameter('time_update', openapi.IN_QUERY, description="Time of the last update of the task", type=openapi.TYPE_STRING),
            openapi.Parameter('tag', openapi.IN_QUERY, description="Tag of the task", type=openapi.TYPE_STRING),
        ],
        responses={200: TasksSerializer(many=True)})
    def get(self, request):
        #'id', 'title', 'content', 'day_to_do', 'done'

        try:
            title = request.query_params.get('title', None)
            content = request.query_params.get('content', None)
            day_to_do = request.query_params.get('day_to_do', None)
            done = request.query_params.get('done', None)
            id = request.query_params.get('id', None)
            time_update = request.query_params.get('time_update', None)
            tag = request.query_params.get('tag', None)
            tasks = Tasks.objects.all().order_by('-time_update')
            user = request.user
            tasks = tasks.filter(username=user.email, done=False)
            if title:
                tasks = tasks.filter(title=title)
            if tag:
                tasks = tasks.filter(tag=tag)
            if content:
                tasks = tasks.filter(content=content)
            if day_to_do:
                tasks = tasks.filter(day_to_do=day_to_do)
            if done:
                tasks = tasks.filter(done=done)
            if id:
                tasks = tasks.filter(id=id)
            if time_update:
                tasks = tasks.filter(time_update=time_update)
            serializer = TasksSerializer(tasks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=TasksSerializer, responses={201: TasksSerializer()})
    def post(self, request):
        serializer = TasksSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Task added successfully', 'post': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={204: 'Task deleted successfully', 404: 'Task does not exist', 400: 'Invalid data'},
    )
    def delete(self, request):
        """
        Удалить задачу
        """
        task_id = request.data.get('id')
        if task_id:
            try:
                task = Tasks.objects.get(pk=task_id)
                task.delete()
                return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({'error': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Task id is required'}, status=status.HTTP_400_BAD_REQUEST)

class ArchiveTasksAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Title of the task", type=openapi.TYPE_STRING),
            openapi.Parameter('day_to_do', openapi.IN_QUERY, description="Day to do the task", type=openapi.TYPE_STRING),
            openapi.Parameter('done', openapi.IN_QUERY, description="Whether the task is done or not", type=openapi.TYPE_STRING),
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the task", type=openapi.TYPE_INTEGER),
            openapi.Parameter('time_update', openapi.IN_QUERY, description="Time of the last update of the task", type=openapi.TYPE_STRING),
            openapi.Parameter('tag', openapi.IN_QUERY, description="Tag of the task", type=openapi.TYPE_STRING),
        ],
        responses={200: TasksSerializer(many=True)})
    def get(self, request):
        #'id', 'title', 'content', 'day_to_do', 'done'
        try:
            title = request.query_params.get('title', None)
            content = request.query_params.get('content', None)
            day_to_do = request.query_params.get('day_to_do', None)
            done = request.query_params.get('done', None)
            id = request.query_params.get('id', None)
            time_update = request.query_params.get('time_update', None)
            tag = request.query_params.get('tag', None)
            tasks = Tasks.objects.all().order_by('-time_update')
            user = request.user
            tasks = tasks.filter(username=user.email, done=True)
            if title:
                tasks = tasks.filter(title=title)
            if tag:
                tasks = tasks.filter(tag=tag)
            if content:
                tasks = tasks.filter(content=content)
            if day_to_do:
                tasks = tasks.filter(day_to_do=day_to_do)
            if done:
                tasks = tasks.filter(done=done)
            if id:
                tasks = tasks.filter(id=id)
            if time_update:
                tasks = tasks.filter(time_update=time_update)
            serializer = TasksSerializer(tasks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={204: 'Task deleted successfully', 404: 'Task does not exist', 400: 'Invalid data'},
    )
    def delete(self, request):
        """
        Удалить задачу
        """
        task_id = request.data.get('id')
        if task_id:
            try:
                task = Tasks.objects.get(pk=task_id)
                task.delete()
                return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({'error': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Task id is required'}, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()
class MyLoginView(LoginView):
    form_class = AuthenticationForm
class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            return redirect('home')
        return redirect('invalid_verify')
    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(email=email, password=password)
            send_email_for_verify(request, user)
            return redirect('confirm_email')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)
