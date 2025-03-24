from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

# -------------- Gallery models ----------------


class GalleryCategory(models.Model):
    """
    Model representing categories for gallery images.
    Used for filtering and organizing images in the gallery.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # URL-friendly version of the name

    def __str__(self):
        """String representation of the category"""
        return self.name

    class Meta:
        verbose_name_plural = "Gallery Categories"  # Admin display name


class GalleryImage(models.Model):
    """
    Model representing an image in the gallery.
    Each image belongs to a category and can be toggled for visibility.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # Optional description
    # Stores images in gallery/ directory
    image = models.ImageField(upload_to='gallery/')
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.CASCADE,  # Delete images when category is deleted
        related_name='images'  # Access as category.images.all()
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True)  # Automatically set on creation
    is_visible = models.BooleanField(
        default=True)  # Control display on website

    def __str__(self):
        """String representation of the image"""
        return self.title

    class Meta:
        ordering = ['-uploaded_at']  # Newest images first


# -------------- News models ----------------

class NewsCategory(models.Model):
    """
    Model representing categories for news articles.
    Used for organizing articles by topic.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # URL-friendly version of the name

    def __str__(self):
        """String representation of the category"""
        return self.name

    class Meta:
        verbose_name_plural = "News Categories"  # Admin display name


class NewsArticle(models.Model):
    """
    Model representing a news article.
    Includes fields for content, metadata, and publishing control.
    """
    title = models.CharField(max_length=200)
    # Auto-generated from title if not provided
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.CASCADE,  # Delete articles when category is deleted
        related_name='articles'  # Access as category.articles.all()
    )
    image = models.ImageField(upload_to='news/')  # Featured image
    excerpt = models.TextField(
        max_length=300,
        help_text="A short summary of the article (max 300 characters)"
    )
    content = models.TextField()  # Main article content
    date_published = models.DateField()  # When the article was/will be published
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this article at the top of the news page"
    )
    is_published = models.BooleanField(default=True)  # Control visibility
    created_at = models.DateTimeField(
        auto_now_add=True)  # When record was created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updates on save

    def save(self, *args, **kwargs):
        """
        Override save method to:
        1. Auto-generate slug from title if not provided
        2. Ensure only one article is featured at a time
        """
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # Ensure only one featured article by unfeaturing all others
        if self.is_featured:
            NewsArticle.objects.filter(
                is_featured=True).update(is_featured=False)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL to access the article detail"""
        return reverse('news_detail', args=[self.slug])

    def __str__(self):
        """String representation of the article"""
        return self.title

    class Meta:
        ordering = ['-date_published']  # Newest articles first


# -------------- Calendar models ----------------

class EventCategory(models.Model):
    """
    Model representing categories for race events.
    Used for organizing events by type (e.g., GT Series, Rally, etc.)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # URL-friendly version of the name

    def __str__(self):
        """String representation of the category"""
        return self.name

    class Meta:
        verbose_name_plural = "Event Categories"  # Admin display name


class RaceEvent(models.Model):
    """
    Model representing a racing event.
    Includes event details, dates, and championship information.
    """
    title = models.CharField(max_length=200)  # Event name
    venue = models.CharField(max_length=200)  # Circuit or location name
    location = models.CharField(
        max_length=200, help_text="City, Province")  # Geographic location
    start_date = models.DateField()  # When the event begins
    # Optional end date for multi-day events
    end_date = models.DateField(blank=True, null=True)
    round_number = models.PositiveSmallIntegerField(
        blank=True, null=True)  # Championship round number
    championship = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. SA GT National Championship"
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,  # Delete events when category is deleted
        related_name='events'  # Access as category.events.all()
    )
    description = models.TextField(blank=True)  # Optional detailed description
    is_active = models.BooleanField(default=True)  # Control display on website

    def __str__(self):
        """String representation of the event"""
        return f"{self.title} - {self.start_date}"

    @property
    def is_upcoming(self):
        """
        Returns whether the event is in the future.
        For multi-day events, checks if the end date is in the future.
        """
        today = timezone.now().date()
        if self.end_date:
            return self.end_date >= today
        return self.start_date >= today

    @property
    def get_date_display(self):
        """
        Returns a formatted string of the event date(s).
        For multi-day events, returns a range (e.g., "15-17").
        """
        if self.end_date:
            if self.start_date.month == self.end_date.month:
                return f"{self.start_date.day}-{self.end_date.day}"
            else:
                return f"{self.start_date.day}-{self.end_date.day}"
        return f"{self.start_date.day}"

    @property
    def get_month_display(self):
        """Returns the abbreviated month name in uppercase (e.g., "JAN")"""
        return self.start_date.strftime('%b').upper()

    class Meta:
        ordering = ['start_date']  # Order by date, earliest first


# Note: EventCategory and RaceEvent models are duplicated in the original file.
# The duplicates are retained here to match the original, but in practice,
# one set would be removed.


# -------------- Team models ----------------

class TeamDepartment(models.Model):
    """
    Model representing different departments in the racing team.
    Used for organizing team members by role or department.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # URL-friendly version of the name
    display_order = models.PositiveSmallIntegerField(
        default=0)  # Control display order

    def __str__(self):
        """String representation of the department"""
        return self.name

    class Meta:
        ordering = ['display_order']  # Order by specified display order
        verbose_name_plural = "Team Departments"  # Admin display name


class TeamMember(models.Model):
    """
    Model representing a team member.
    Includes personal details, role, and department assignment.
    """
    name = models.CharField(
        max_length=200,
        help_text="Full name of the team member"
    )
    role = models.CharField(max_length=100)  # Position or title
    photo = models.ImageField(upload_to='team/')  # Profile photo
    bio = models.TextField()  # Biographical information
    department = models.ForeignKey(
        TeamDepartment,
        on_delete=models.CASCADE,  # Delete members when department is deleted
        related_name='members'  # Access as department.members.all()
    )
    display_order = models.PositiveSmallIntegerField(
        default=0)  # Control display order
    is_active = models.BooleanField(default=True)  # Control display on website

    def __str__(self):
        """String representation of the team member"""
        return self.name

    class Meta:
        # Order by department, then display order
        ordering = ['department', 'display_order']
        verbose_name_plural = "Team Members"  # Admin display name


class TeamMemberSkill(models.Model):
    """
    Model representing skills or expertise of team members.
    Used to highlight specific capabilities and experiences.
    """
    team_member = models.ForeignKey(
        TeamMember,
        on_delete=models.CASCADE,  # Delete skills when team member is deleted
        related_name='skills'  # Access as member.skills.all()
    )
    name = models.CharField(max_length=50)  # Name of the skill or expertise

    def __str__(self):
        """String representation of the skill"""
        return f"{self.name} ({self.team_member})"

    class Meta:
        verbose_name_plural = "Team Member Skills"  # Admin display name
