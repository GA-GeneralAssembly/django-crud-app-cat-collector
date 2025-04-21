from django.shortcuts import render, redirect
from .models import Cat
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import FeedingForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


# Import HttpResponse to send text-based responses
# from django.http import HttpResponse


# Create your views here.

# Define the home view function

# def home(request):
#     # Send a simple HTML response
#     return render(request, 'home.html')

class Home(LoginView):
    template_name = 'home.html'


def about(request):
    return render(request, 'about.html')


@login_required
def cat_index(request):
    cats = Cat.objects.filter(user=request.user)
    # You could also retrieve the logged in user's cats like this
    # cats = request.user.cat_set.all()
    return render(request, 'cats/index.html', { 'cats': cats })

@login_required
def cat_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {
        # include the cat and feeding_form in the context
        'cat': cat, 'feeding_form': feeding_form
    })


@login_required
def add_feeding(request, cat_id):
    # create a ModelForm instance using the data in request.POST
    form = FeedingForm(request.POST)
    # validate the form
    if form.is_valid():
        # don't save the form to the db until it
        # has the cat_id assigned
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('cat-detail', cat_id=cat_id)


def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect('cat-index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)
    # Same as: 
    # return render(
    #     request, 
    #     'signup.html',
    #     {'form': form, 'error_message': error_message}
    # )


class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    # fields = '__all__'
    # success_url = '/cats/'
    fields = ['name', 'breed', 'description', 'age']
    # This inherited method is called when a
    # valid cat form is being submitted
    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)


class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']


class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'
