from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from .models import Watchlist, Readlist,Movie, Book, User, ActivityFeed, MBTIType, ReadlistItem, WatchlistItem
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages  # Import for messages
from django.urls import reverse



def home(request):
    return render(request, 'home.html')

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # This retrieves the email
            password = request.POST.get('password')  # Get the password directly from POST data
            
            # Use the username parameter instead of email in authenticate
            user = authenticate(request, username=email, password=password)  # Change here
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})



# User Logout View
def logout_user(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Watchlist, Readlist, ActivityFeed, User, Feedback
from .forms import FeedbackForm, EditBioForm  # Import the bio form
from django.conf import settings

import os


# Dashboard View
from django.db.models import Q
from .models import Watchlist, Readlist, ActivityFeed
from django.conf import settings

import os
from django.db import connection

from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from website.models import WatchlistItem, ReadlistItem
from .models import PersonalizedList, PersonalizedMovie, PersonalizedBook, Movie, Book
from django.contrib.auth.decorators import login_required
from .forms import PersonalizedListForm, PersonalizedMovieForm, PersonalizedBookForm

from django.shortcuts import get_object_or_404
from .models import PersonalizedList

@login_required
def dashboard(request):
    user = request.user
    avatar_path = user.avatar.url if user.avatar else 'default_avatar.svg'

    # Raw SQL for watchlist and readlist
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT w.movie_id, w.status, m.title
            FROM website_watchlistitem w
            JOIN website_movie m ON w.movie_id = m.movie_id
            WHERE w.user_id = %s
        """, [user.user_id])
        watchlist = cursor.fetchall()

        cursor.execute("""
            SELECT r.book_id, r.status, b.title
            FROM website_readlistitem r
            JOIN website_book b ON r.book_id = b.book_id
            WHERE r.user_id = %s
        """, [user.user_id])
        readlist = cursor.fetchall()

    # Raw SQL for activity feed
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM website_activityfeed 
            WHERE user_id = %s OR user_id IN (
                SELECT from_user_id FROM website_user_following WHERE from_user_id = %s
            )
            ORDER BY created_at DESC LIMIT 10
        """, [user.user_id, user.user_id])
        activity_feed = cursor.fetchall()

    # Follower and following counts
    followers_count = user.followers.count()  # Keeping ORM here for simplicity
    following_count = user.following.count()

    # Handle bio form submission
    if request.method == 'POST':
        form = EditBioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EditBioForm(instance=user)

    # Process watchlist and readlist into usable context
    watchlist_items = [
        {'movie_id': item[0], 'status': item[1], 'title': item[2]}
        for item in watchlist
    ]
    readlist_items = [
        {'book_id': item[0], 'status': item[1], 'title': item[2]}
        for item in readlist
    ]

    # Fetch personalized lists
    personalized_lists = PersonalizedList.objects.filter(user=user).prefetch_related('movies', 'books')

    # Prepare personalized list context
    personalized_list_data = []
    for p_list in personalized_lists:
        movies = [
            {'title': movie.movie.title, 'rating': movie.rating, 'review': movie.review}
            for movie in p_list.movies.all()
        ]
        books = [
            {'title': book.book.title, 'rating': book.rating, 'review': book.review}
            for book in p_list.books.all()
        ]
        personalized_list_data.append({
            'id' : p_list.id,
            'list_name': p_list.list_name,
            'created_at': p_list.created_at,
            'movies': movies,
            'books': books,
        })

    context = {
        'username': user.username,
        'bio': user.bio,
        'mbti_type': user.mbti_type.mbti_type if user.mbti_type else 'Not set',
        'avatar_path': avatar_path,
        'watchlist': watchlist_items,
        'readlist': readlist_items,
        'activity_feed': activity_feed,
        'followers_count': followers_count,
        'following_count': following_count,
        'form': form,
        'personalized_lists': personalized_list_data,
    }

    return render(request, 'dashboard.html', context)

@login_required
def create_list(request):
    if request.method == 'POST':
        form = PersonalizedListForm(request.POST)
        if form.is_valid():
            personalized_list = form.save(commit=False)
            personalized_list.user = request.user
            personalized_list.save()
            return redirect('dashboard')
    else:
        form = PersonalizedListForm()
    return render(request, 'create_list.html', {'form': form})
# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PersonalizedList

@login_required
def delete_list(request, list_id):
    # Get the personalized list
    personalized_list = get_object_or_404(PersonalizedList, id=list_id)
    
    # Ensure that the current user is the owner of the list
    if personalized_list.user == request.user:
        personalized_list.delete()
        # Redirect to a page where the user can see their updated lists (e.g., dashboard)
        return redirect('dashboard')  # Adjust URL to where you want to redirect
    else:
        # Optionally, handle the case where the user is not the owner
        return redirect('dashboard')  # Redirect if unauthorized

@login_required
def add_movie_to_list(request, list_id):
    personalized_list = get_object_or_404(PersonalizedList, id=list_id, user=request.user)
    if request.method == 'POST':
        form = PersonalizedMovieForm(request.POST)
        if form.is_valid():
            movie_entry = form.save(commit=False)
            movie_entry.personalized_list = personalized_list
            movie_entry.save()
            return redirect('dashboard')
    else:
        form = PersonalizedMovieForm()
    return render(request, 'add_movie.html', {'form': form, 'list': personalized_list})

@login_required
def add_book_to_list(request, list_id):
    personalized_list = get_object_or_404(PersonalizedList, id=list_id, user=request.user)
    if request.method == 'POST':
        form = PersonalizedBookForm(request.POST)
        if form.is_valid():
            book_entry = form.save(commit=False)
            book_entry.personalized_list = personalized_list
            book_entry.save()
            return redirect('dashboard')
    else:
        form = PersonalizedBookForm()
    return render(request, 'add_book.html', {'form': form, 'list': personalized_list})



from django.shortcuts import render
from .models import ActivityFeed

def activity(request):
    user = request.user
    
    # Activity Feed
    activity_feed = ActivityFeed.objects.filter(
        Q(user=user) | Q(user__in=user.following.all())
    ).order_by('-created_at')[:10]

    context = {
        'activity_feed': activity_feed,
    }
    return render(request, 'activity.html', context)

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, user_id=user_id)
    current_user = request.user

    if current_user == user_to_follow:
        return redirect('other_dashboard', user_id=user_id)  # Prevent self-following

    if user_to_follow in current_user.following.all():
        # Unfollow the user
        current_user.following.remove(user_to_follow)
        user_to_follow.followers.remove(current_user)  # Remove from followers as well
        ActivityFeed.objects.create(user=current_user, action=f"unfollowed {user_to_follow.username}")
    else:
        # Follow the user
        current_user.following.add(user_to_follow)
        user_to_follow.followers.add(current_user)  # Add to followers as well
        ActivityFeed.objects.create(user=current_user, action=f"followed {user_to_follow.username}")

    # Refresh both users to ensure counts are updated
    current_user.refresh_from_db()
    user_to_follow.refresh_from_db()

    # Recalculate follower and following counts after the update
    followers_count = user_to_follow.followers.count()
    following_count = current_user.following.count()

    # Redirect to the user's profile with the updated counts
    return redirect('other_dashboard', user_id=user_id)
# Books View using raw SQL
from django.db import connection
from django.shortcuts import render
from django.db import connection
from django.shortcuts import render

def books_view(request):
    # Execute the raw SQL query to fetch books and their MBTI preferences
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.description, b.publication_year, b.image,
                   mbti_first.mbti_type AS first_preference, 
                   mbti_second.mbti_type AS second_preference, 
                   mbti_third.mbti_type AS third_preference
            FROM website_book b
            LEFT JOIN website_mbtitype mbti_first ON b.first_preference_id = mbti_first.mbti_type_id
            LEFT JOIN website_mbtitype mbti_second ON b.second_preference_id = mbti_second.mbti_type_id
            LEFT JOIN website_mbtitype mbti_third ON b.third_preference_id = mbti_third.mbti_type_id
            ORDER BY b.title
        """)
        books = cursor.fetchall()

    # Process the raw query result into a list of dictionaries (for easier template access)
    books_list = []
    for book in books:
        books_list.append({
            'book_id': book[0],
            'title': book[1],
            'author': book[2],
            'description': book[3],
            'publication_year': book[4],
            'image': book[5],
            'first_preference': book[6],
            'second_preference': book[7],
            'third_preference': book[8],
        })

    # Pass books to the template
    context = {
        'books': books_list,
    }

    return render(request, 'books.html', context)

from django.db import connection

def movies_view(request):
    # Execute the raw SQL query to fetch movies and their MBTI preferences
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.movie_id, m.title, m.description, m.release_date, m.image,
                   mbti_first.mbti_type AS first_preference, 
                   mbti_second.mbti_type AS second_preference, 
                   mbti_third.mbti_type AS third_preference
            FROM website_movie m
            LEFT JOIN website_mbtitype mbti_first ON m.first_preference_id = mbti_first.mbti_type_id
            LEFT JOIN website_mbtitype mbti_second ON m.second_preference_id = mbti_second.mbti_type_id
            LEFT JOIN website_mbtitype mbti_third ON m.third_preference_id = mbti_third.mbti_type_id
            ORDER BY m.title
        """)
        # Fetch all results as a dictionary-like object
        movies = cursor.fetchall()

        # Convert raw results into a list of dictionaries
        movie_list = []
        for movie in movies:
            movie_dict = {
                'movie_id': movie[0],
                'title': movie[1],
                'description': movie[2],
                'release_date': movie[3],
                'image': movie[4],
                'first_preference': movie[5],
                'second_preference': movie[6],
                'third_preference': movie[7],
            }
            movie_list.append(movie_dict)

    # Pass movies to the template
    context = {
        'movies': movie_list,
    }

    return render(request, 'movies.html', context)

@login_required
@require_POST
def add_to_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    # Check if the movie is already in the user's watchlist
    if not WatchlistItem.objects.filter(user=request.user, movie=movie).exists():
        WatchlistItem.objects.create(user=request.user, movie=movie, status='not_started')
        message = f"'{movie.title}' has been added to your watchlist."
        # Log the action of adding a movie
        ActivityFeed.objects.create(user=request.user, action=f"added '{movie.title}' to their watchlist.")
    else:
        message = f"'{movie.title}' is already in your watchlist."

    return redirect('dashboard')

@login_required
@require_POST
def add_to_readlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # Check if the book is already in the user's readlist
    if not ReadlistItem.objects.filter(user=request.user, book=book).exists():
        ReadlistItem.objects.create(user=request.user, book=book, status='not_started')
        message = f"'{book.title}' has been added to your readlist."
        # Log the action of adding a book
        ActivityFeed.objects.create(user=request.user, action=f"added '{book.title}' to their readlist.")
    else:
        message = f"'{book.title}' is already in your readlist."

    return redirect('dashboard')

@login_required
@require_POST
def remove_from_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    # Find and delete the WatchlistItem
    watchlist_item = WatchlistItem.objects.filter(user=request.user, movie=movie).first()
    if watchlist_item:
        watchlist_item.delete()
        messages.success(request, f"'{movie.title}' has been removed from your watchlist.")
        # Log the removal action
        ActivityFeed.objects.create(user=request.user, action=f"removed '{movie.title}' from their watchlist.")
    else:
        messages.warning(request, f"'{movie.title}' is not in your watchlist.")

    return redirect('dashboard')

@login_required
@require_POST
def remove_from_readlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # Find and delete the ReadlistItem
    readlist_item = ReadlistItem.objects.filter(user=request.user, book=book).first()
    if readlist_item:
        readlist_item.delete()
        messages.success(request, f"'{book.title}' has been removed from your readlist.")
        # Log the removal action
        ActivityFeed.objects.create(user=request.user, action=f"removed '{book.title}' from their readlist.")
    else:
        messages.warning(request, f"'{book.title}' is not in your readlist.")

    return redirect('dashboard')


@login_required
def update_watchlist_status(request, movie_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        watchlist_item = get_object_or_404(WatchlistItem, user=request.user, movie__movie_id=movie_id)
        watchlist_item.status = status
        watchlist_item.save()
    return redirect('dashboard')

@login_required
def update_readlist_status(request, book_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        readlist_item = get_object_or_404(ReadlistItem, user=request.user, book__book_id=book_id)
        readlist_item.status = status
        readlist_item.save()
    return redirect('dashboard')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CompatibilityScore, User, MBTIType
from django.db.models import Q
def compare_mbti_types(user_1, user_2):
    """
    Calculate compatibility score between two users based on their MBTI types.

    Args:
        user_1 (User): First user instance.
        user_2 (User): Second user instance.

    Returns:
        float: Compatibility score (0 to 100).
    """
    if not user_1.mbti_type or not user_2.mbti_type:
        return 0.0  # Return 0 if either user doesn't have an MBTI type assigned.

    mbti_type_1 = user_1.mbti_type.mbti_type
    mbti_type_2 = user_2.mbti_type.mbti_type

    if len(mbti_type_1) != 4 or len(mbti_type_2) != 4:
        return 0.0  # Return 0 if MBTI types are not valid 4-character strings.

    # Compatibility scoring
    compatibility_score = 0
    dimensions = ['I/E', 'S/N', 'T/F', 'J/P']

    for i in range(4):  # Compare each character in the MBTI type
        if mbti_type_1[i] == mbti_type_2[i]:
            compatibility_score += 1  # Fully compatible on this dimension

    # Normalize to 0-100 scale
    return compatibility_score * 25  # 4 dimensions, each worth 25 points

from .models import CompatibilityScore, User

@login_required
def calculate_compatibility(request, user_id):
    user = request.user  # Current logged-in user
    compared_user = get_object_or_404(User, id=user_id)  # User to compare with

    # Get the MBTI types of both users
    user_mbti = getattr(user.mbti_type, 'mbti_type', None)
    compared_user_mbti = getattr(compared_user.mbti_type, 'mbti_type', None)

    if user_mbti and compared_user_mbti:
        # Calculate compatibility score
        score = compare_mbti_types(user_mbti, compared_user_mbti)

        # Update or create the compatibility score (user -> compared_user)
        CompatibilityScore.objects.update_or_create(
            user=user,
            compared_user=compared_user,
            defaults={'score': score}
        )
        # Update or create the reverse compatibility score (compared_user -> user)
        CompatibilityScore.objects.update_or_create(
            user=compared_user,
            compared_user=user,
            defaults={'score': score}
        )

        return redirect('other_dashboard', user_id=compared_user.id)

    # Redirect with an error message if MBTI types are missing
    messages.error(request, "MBTI types are missing for one or both users.")
    return redirect('other_dashboard', user_id=compared_user.id)

from django.contrib import messages

# View to submit feedback
@login_required
def give_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.feedback_giver = request.user  # Link the feedback to the logged-in user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('about')  # Redirect to the 'about' page or desired location
        else:
            messages.error(request, "There was an error with your submission. Please try again.")
    else:
        form = FeedbackForm()

    return render(request, 'feedback/give_feedback.html', {'form': form})

# View to display all feedback on the about page
from django.contrib import messages

from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm
from .models import Feedback

from django.db import connection
from django.contrib import messages
from django.shortcuts import render, redirect

def about(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.feedback_giver = request.user  # Set the feedback giver to the logged-in user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('about')  # Refresh the page to show the new feedback
        else:
            messages.error(request, "There was an error. Please try again.")
    else:
        form = FeedbackForm()

    # Using raw SQL to fetch feedbacks along with the feedback giver's username
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT fb.feedback_id, fb.message, fb.feedback_giver_id, au.username, fb.created_at
            FROM website_feedback fb
            INNER JOIN website_user au ON fb.feedback_giver_id = au.user_id
            ORDER BY fb.created_at DESC
        """)
        feedbacks = [
            {
                'id': row[0],
                'message': row[1],
                'feedback_giver_id': row[2],
                'feedback_giver_name': row[3],  # Include username
                'created_at': row[4],
            }
            for row in cursor.fetchall()
        ]

    return render(request, 'about.html', {'feedbacks': feedbacks, 'form': form})

from django.db import connection
from django.shortcuts import render
from django.db import connection
from django.shortcuts import render
from django.utils.timezone import now

@login_required
def top_picks(request):
    # Ensure the user has an MBTI type assigned
    user_mbti_type_id = request.user.mbti_type_id

    if user_mbti_type_id is None:
        return render(request, 'error.html', {'message': 'MBTI type not set.'})

    # Fetch movies matching the user's MBTI preferences
    movies = Movie.objects.raw("""
        SELECT * FROM website_movie
        WHERE first_preference_id = %s
           OR second_preference_id = %s
           OR third_preference_id = %s
    """, [user_mbti_type_id, user_mbti_type_id, user_mbti_type_id])

    # Fetch books matching the user's MBTI preferences
    books = Book.objects.raw("""
        SELECT * FROM website_book
        WHERE first_preference_id = %s
           OR second_preference_id = %s
           OR third_preference_id = %s
    """, [user_mbti_type_id, user_mbti_type_id, user_mbti_type_id])

    # Pass as 'top_movies' and 'top_books' to match the template
    return render(request, 'top_picks.html', {'top_movies': movies, 'top_books': books})

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import User, MBTIType, Movie, Book

@login_required
def connect(request):
    # Get the current logged-in user
    current_user = request.user
    
    # If there's a search query, filter users by MBTI type
    mbti_filter = request.GET.get('mbti_type', None)
    
    # Fetch all users except the current one
    users = User.objects.exclude(user_id=current_user.user_id)  # Use `user_id` as primary key

    # Filter users by MBTI type if a search is provided
    if mbti_filter:
        users = users.filter(mbti_type__mbti_type=mbti_filter)
    
    # Get all MBTI types for the search filter dropdown
    mbti_types = MBTIType.objects.all()

    context = {
        'users': users,
        'mbti_types': mbti_types,
        'current_user': current_user,
    }
    return render(request, 'connect.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, WatchlistItem, ReadlistItem, CompatibilityScore

def compare_mbti_types(mbti_type_1, mbti_type_2):
    """
    Calculate compatibility score between two MBTI types using weighted dimensions.

    Args:
        mbti_type_1 (str): MBTI type of user 1.
        mbti_type_2 (str): MBTI type of user 2.

    Returns:
        float: Compatibility score (0 to 100).
    """
    if not mbti_type_1 or not mbti_type_2:
        return 0.0

    if len(mbti_type_1) != 4 or len(mbti_type_2) != 4:
        return 0.0

    # Weighting for each dimension
    weights = [0.25, 0.30, 0.30, 0.15]  # I/E, S/N, T/F, J/P

    # Compatibility scoring
    compatibility_score = 0
    for i in range(4):
        if mbti_type_1[i] == mbti_type_2[i]:
            compatibility_score += weights[i]  # Fully compatible for this dimension
        elif (i == 0 and (mbti_type_1[i] in 'IE' and mbti_type_2[i] in 'IE')) or \
             (i == 3 and (mbti_type_1[i] in 'JP' and mbti_type_2[i] in 'JP')):
            # Bonus points for complementary opposites in I/E and J/P dimensions
            compatibility_score += weights[i] * 0.5

    # Normalize to 0-100 scale
    return compatibility_score * 100
@login_required
def other_dashboard(request, user_id):
    selected_user = get_object_or_404(User, user_id=user_id)

    # Ensure compatibility score is calculated or updated
    user_mbti = getattr(request.user.mbti_type, 'mbti_type', None)
    selected_user_mbti = getattr(selected_user.mbti_type, 'mbti_type', None)

    if user_mbti and selected_user_mbti:
        score = compare_mbti_types(user_mbti, selected_user_mbti)

        # Use raw SQL to insert or update compatibility score
        with connection.cursor() as cursor:
            # Update or insert the compatibility score (request.user -> selected_user)
            cursor.execute("""
                INSERT INTO website_compatibilityscore (user_id, compared_user_id, score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE score = VALUES(score)
            """, [request.user.user_id, selected_user.user_id, score])

            # Update or insert the reverse compatibility score (selected_user -> request.user)
            cursor.execute("""
                INSERT INTO website_compatibilityscore (user_id, compared_user_id, score)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE score = VALUES(score)
            """, [selected_user.user_id, request.user.user_id, score])

    # Calculate followers, following, and fetch lists
    followers_count = selected_user.followers.count()
    following_count = selected_user.following.count()

    with connection.cursor() as cursor:
        # Watchlist
        cursor.execute("""
            SELECT w.movie_id, w.status, m.title
            FROM website_watchlistitem w
            JOIN website_movie m ON w.movie_id = m.movie_id
            WHERE w.user_id = %s
        """, [selected_user.user_id])
        watchlist = cursor.fetchall()

        # Readlist
        cursor.execute("""
            SELECT r.book_id, r.status, b.title
            FROM website_readlistitem r
            JOIN website_book b ON r.book_id = b.book_id
            WHERE r.user_id = %s
        """, [selected_user.user_id])
        readlist = cursor.fetchall()

    # Process lists
    watchlist_items = [{'movie_id': item[0], 'status': item[1], 'title': item[2]} for item in watchlist]
    readlist_items = [{'book_id': item[0], 'status': item[1], 'title': item[2]} for item in readlist]

    # Fetch personalized lists for selected_user
    personalized_lists = PersonalizedList.objects.filter(user=selected_user).prefetch_related('movies', 'books')


    # Prepare personalized list context
    personalized_list_data = []
    for p_list in personalized_lists:
        movies = [
            {'title': movie.movie.title, 'rating': movie.rating, 'review': movie.review}
            for movie in p_list.movies.all()
        ]
        books = [
            {'title': book.book.title, 'rating': book.rating, 'review': book.review}
            for book in p_list.books.all()
        ]
        personalized_list_data.append({
            'id' : p_list.id,
            'list_name': p_list.list_name,
            'created_at': p_list.created_at,
            'movies': movies,
            'books': books,
        })

    # Fetch compatibility score
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT score FROM website_compatibilityscore
            WHERE user_id = %s AND compared_user_id = %s
        """, [request.user.user_id, selected_user.user_id])
        row = cursor.fetchone()
        compatibility_score = row[0] if row else 0

    # Render the dashboard
    context = {
    'selected_user': selected_user,
    'watchlist': watchlist_items,
    'readlist': readlist_items,
    'personalized_lists': personalized_list_data,  # This should match template expectations
    'compatibility_score': compatibility_score,
    'followers_count': followers_count,
    'following_count': following_count,
    }
    return render(request, 'other_dashboard.html', context)