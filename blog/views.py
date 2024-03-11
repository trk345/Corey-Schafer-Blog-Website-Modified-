from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.views import View

# from django.http import HttpResponse
from .models import Post, Category
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q, F, Avg
from django import forms


# Create your views here.
# posts = [
#     {
#         'author': 'TRK',
#         'title': 'BlogPost 1',
#         'content': 'First Post Content',
#         'date_posted': 'June 29th, 2023'
#     },
# {
#         'author': 'SRK',
#         'title': 'BlogPost 2',
#         'content': 'Second Post Content',
#         'date_posted': 'June 30th 2023'
#     }
# ]

def home(request):
    context = {'posts':Post.objects.all()}
    return render(request,'blog/home.html',context)

class PostListView(ListView): #making class based view
    model = Post
    template_name = 'blog/home.html'  #<app>/<model>_<viewtype>.html
    context_object_name = 'posts' #make sure to get the var name right
    ordering = ['-date_posted'] #sort the blogs according to the date posted,'-' gives reverse order
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Retrieve all categories
        return context

class UserPostListView(ListView): #making class based view
    model = Post
    template_name = 'blog/user_posts.html'  #<app>/<model>_<viewtype>.html
    context_object_name = 'posts' #make sure to get the var name right
    # ordering = ['-date_posted'] #sort the blogs according to the date posted,'-' gives reverse order
    paginate_by = 5
    def get_queryset(self):
        user = get_object_or_404(User,username = self.kwargs.get('username'))
        return Post.objects.filter(author = user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Retrieve all categories
        return context

class PostDetailView(DetailView): #making class based view
    model = Post
    def get(self, request, *args, **kwargs):
        # Get the post object
        self.object = self.get_object()

        # Increment the view count only if the current user is not the author
        if not self.object.author == self.request.user:
            self.object.views += 1
            self.object.save()

        # Continue with the default behavior
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)



class PostCreateView(LoginRequiredMixin, CreateView): #making class based view;
# loginrequiredmixin ensures a user to be logged in before creating a post as
# login_reuired decorator can't be used for classes
    model = Post
    fields = ['title', 'category', 'content', 'image']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.all().order_by('name')
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): #userpassestestmixin
    model = Post                              #ensures that a user can't update another user's post
    fields = ['title', 'category', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object() #this gets the post that we r tying to update
        if self.request.user == post.author: #checks if the current user is the author of the post
            return True                      #that we are trying to update
        return False

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.pk})
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object() #this gets the post that we r tying to update
        if self.request.user == post.author: #checks if the current user is the author of the post
            return True                      #that we are trying to update
        return False

class CategoryDetailView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Post.objects.filter(category_id=category_id).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(id=self.kwargs['category_id'])
        total_likes = 0
        for post in context['posts']:
            total_likes += post.number_of_likes()
        context['total_likes'] = total_likes
        return context

def search_view(request):
    query = request.GET.get('query')

    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(author__username__icontains=query)
        ).annotate(author_username=F('author__username'), category_name=F('category__name'))

    else:
        results = []

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'blog/search_results.html', context)

def blog_like(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=pk)
        if post.likes.filter(id=request.user.id):
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect('blog-home')
    else:
        return redirect('blog-home')


def about(request):
    return render(request,'blog/about.html',{'title': 'About'})