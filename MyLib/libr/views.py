from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookForm
from .models import Book


def home(request):
    if request.user.is_authenticated:
        return redirect('user_libr')
    else:
        return render(request, 'libr/home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'libr/signup_user.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('user_libr')
            except IntegrityError:
                return render(request, 'libr/signup_user.html',
                              {'form': UserCreationForm(), 'error': 'That user name already has been taken.'})

        else:
            return render(request, 'libr/signup_user.html',
                          {'form': UserCreationForm(), 'error': 'Passwords did not match'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'libr/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'libr/login_user.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password did not match '})
        else:
            login(request, user)
            return redirect('user_libr')


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def create_book(request):
    if request.method == 'GET':
        return render(request, 'libr/create_book.html', {'form': BookForm()})
    else:
        try:
            form = BookForm(request.POST)
            new_book = form.save(commit=False)
            new_book.user = request.user
            new_book.save()
            return redirect('user_libr')
        except ValueError:
            return render(request, 'libr/create_book.html',
                          {'form': BookForm(), 'error': 'Bad data passed in. Try again'})


def user_libr(request):
    # Getting search parameters from the form
    search_title = request.GET.get('title', '')
    search_author = request.GET.get('author', '')
    search_genre = request.GET.get('genre', '')
    search_year = request.GET.get('year', '')
    status_filter = request.GET.get('status', 'all')

    # Getting all user books
    all_books = Book.objects.filter(user=request.user)

    # Applying filters with search parameters
    books = all_books.filter(
        title__icontains=search_title,
        author__icontains=search_author,
        genre__icontains=search_genre,
        year__icontains=search_year
    )

    # Getting number of read and unread books
    read_books_count = all_books.filter(is_read=True).count()
    unread_books_count = all_books.filter(is_read=False).count()

    # Filter of books by status ("read" or "unread")
    if status_filter == 'read':
        books = books.filter(is_read=True)
    elif status_filter == 'unread':
        books = books.filter(is_read=False)

    return render(request, 'libr/user_libr.html',
                  {'books': books,
                   'read_books_count': read_books_count,
                   'unread_books_count': unread_books_count,
                   'search_title': search_title,
                   'search_author': search_author,
                   'search_genre': search_genre,
                   'search_year': search_year,
                   'status_filter': status_filter})


def book_detail(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk, user=request.user)
    if request.method == 'GET':
        form = BookForm(instance=book)
        return render(request, 'libr/book_detail.html', {'book': book, 'form': form})
    else:
        try:
            form = BookForm(request.POST, instance=book)
            form.save()
            return redirect('user_libr')
        except ValueError:
            return render(request, 'libr/book_detail.html', {'book': book, 'form': form, 'error': 'Bad info'})


def book_delete(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('user_libr')
