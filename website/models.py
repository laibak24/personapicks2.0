from django.db import models
from django.contrib.auth.models import AbstractUser

# MBTI Type Model
class MBTIType(models.Model):
    MBTI_CHOICES = [
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP')
    ]

    mbti_type_id = models.AutoField(primary_key=True)
    mbti_type = models.CharField(max_length=4, choices=MBTI_CHOICES, unique=True)

    def __str__(self):
        return self.mbti_type

# Custom User Model
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, default="")
    email = models.EmailField(unique=True, default="")
    mbti_type = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True)
    avatar = models.ImageField(upload_to='avatars/', default="avatar.svg", null=True)
    # Add this to the User model
    bio = models.TextField(blank=True, default="Tell others about yourself!")
    # Follow feature
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

#Activity Model
class ActivityFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)  # e.g., "added 'Inception' to their watchlist"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at}"

# Movie Model
class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='media/movie_images/', default='default_movie.jpg')

    # Adding MBTI preferences
    first_preference = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True, related_name='preferred_movies_first')
    second_preference = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True, related_name='preferred_movies_second')
    third_preference = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True, related_name='preferred_movies_third')

    def __str__(self):
        return self.title

# Book Model
class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    publication_year = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='book_images/', default='default_book.jpg')

    # Adding MBTI preferences
    first_preference = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True, related_name='preferred_books_first')
    second_preference = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True, related_name='preferred_books_second')
    third_preference = models.ForeignKey(MBTIType, on_delete=models.SET_NULL, null=True, related_name='preferred_books_third')

    def __str__(self):
        return self.title


# Feedback Model
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    feedback_giver = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.feedback_giver}"

# Recommendations Model
class Recommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    recommendation_for_user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    recommended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.recommendation_for_user}"

STATUS_CHOICES = [
    ('not_started', 'Not Started'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
]

# Watchlist Model for Movies
class Watchlist(models.Model):
    watchlist_user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Watchlist of {self.watchlist_user}"

    def save(self, *args, **kwargs):
        # Log activity on save
        if self.pk is None:  # Only for new entries
            ActivityFeed.objects.create(
                user=self.watchlist_user,
                action=f"added movies to their watchlist."
            )
        super().save(*args, **kwargs)

# Readlist Model for Books
class Readlist(models.Model):
    readlist_user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Readlist of {self.readlist_user}"

    def save(self, *args, **kwargs):
        # Log activity on save
        if self.pk is None:  # Only for new entries
            ActivityFeed.objects.create(
                user=self.readlist_user,
                action=f"added books to their readlist."
            )
        super().save(*args, **kwargs)

# Updated Watchlist with an Intermediate Model
class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s watchlist item: {self.movie.title} ({self.status})"

    def save(self, *args, **kwargs):
        # Log activity on save for new items
        if self.pk is None:
            ActivityFeed.objects.create(
                user=self.user,
                action=f"added '{self.movie.title}' to their watchlist."
            )
        super().save(*args, **kwargs)

# Updated Readlist with an Intermediate Model
class ReadlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='readlist_items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s readlist item: {self.book.title} ({self.status})"

    def save(self, *args, **kwargs):
        # Log activity on save for new items
        if self.pk is None:
            ActivityFeed.objects.create(
                user=self.user,
                action=f"added '{self.book.title}' to their readlist."
            )
        super().save(*args, **kwargs)

class CompatibilityScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compatibility_scores')
    compared_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compared_scores')
    score = models.FloatField()

    class Meta:
        unique_together = ('user', 'compared_user')

    def __str__(self):
        return f"Compatibility between {self.user} and {self.compared_user}: {self.score}"

    # Personalized List Model
class PersonalizedList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personalized_lists')
    list_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.list_name}"

# Personalized Movie Entry in the List
class PersonalizedMovie(models.Model):
    personalized_list = models.ForeignKey(PersonalizedList, on_delete=models.CASCADE, related_name='movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 11)])  # Rating from 1 to 10
    review = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.movie.title} in {self.personalized_list.list_name}"

# Personalized Book Entry in the List
class PersonalizedBook(models.Model):
    personalized_list = models.ForeignKey(PersonalizedList, on_delete=models.CASCADE, related_name='books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 11)])  # Rating from 1 to 10
    review = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} in {self.personalized_list.list_name}"