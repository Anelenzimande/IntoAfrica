from .models import GalleryCategory, GalleryImage
from django.shortcuts import render
from .models import NewsArticle, NewsCategory
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import RaceEvent
from .models import TeamDepartment, TeamMember


def index(request):
    """
    Homepage view function.
    Retrieves and renders latest news, upcoming events, and the next race.
    """
    # Get the 2 most recent published news articles
    latest_news = NewsArticle.objects.filter(
        is_published=True).order_by('-date_published')[:2]

    # Get upcoming events for the calendar section
    from django.utils import timezone
    upcoming_events = RaceEvent.objects.filter(
        is_active=True,
        start_date__gte=timezone.now().date()  # Only future events
    ).order_by('start_date')[:5]  # Limit to 5 upcoming events

    # Get the next race (first upcoming race)
    next_race = upcoming_events.first() if upcoming_events.exists() else None

    # Get current year for display
    current_year = timezone.now().year

    # Prepare context data to pass to the template
    context = {
        'latest_news': latest_news,
        'upcoming_events': upcoming_events,
        'current_year': current_year,
        'next_race': next_race
    }

    return render(request, 'Website/index.html', context)


def about(request):
    """
    About page view function.
    Simple view that renders the about page.
    """
    return render(request, 'Website/about.html')


def team(request):
    """
    Team page view function.
    Retrieves team members grouped by departments and prepares for tabbed display.
    """
    # Get all departments ordered by display_order field
    departments = TeamDepartment.objects.all().order_by('display_order')

    # Get all active team members across all departments
    all_members = TeamMember.objects.filter(
        is_active=True).order_by('department', 'display_order')

    # Create list to hold department data with associated members
    department_data = []

    # Add "All" as the first tab - this will show all team members
    department_data.append({
        'department': {
            'name': 'All',
            'slug': 'all'
        },
        'members': all_members
    })

    # Add each department and its members
    for dept in departments:
        # Filter members to only those in this department
        members = TeamMember.objects.filter(
            department=dept,
            is_active=True
        ).order_by('display_order')

        department_data.append({
            'department': dept,
            'members': members
        })

    context = {
        'department_data': department_data,
    }

    return render(request, 'Website/team.html', context)


def gallery(request):
    """
    Gallery page view function.
    Retrieves and displays image categories and images for the gallery.
    """
    # Get all active categories for filtering
    categories = GalleryCategory.objects.all()

    # Get all visible images
    images = GalleryImage.objects.filter(is_visible=True)

    # Check if there are any images to display
    has_images = images.exists()

    context = {
        'categories': categories,
        'images': images,
        'has_images': has_images
    }

    return render(request, 'Website/gallery.html', context)


# Commented out old news view
# def news(request):
#     return render(request, 'Website/news.html')

def news(request):
    """
    News listing page view function.
    Retrieves, filters, and paginates news articles.
    Handles featured articles separately from regular articles.
    """
    # Get all published articles
    articles = NewsArticle.objects.filter(is_published=True)

    # Get featured article (if any) to display prominently
    featured_article = articles.filter(is_featured=True).first()

    # If there's a featured article, exclude it from regular list to avoid duplication
    if featured_article:
        regular_articles = articles.exclude(id=featured_article.id)
    else:
        regular_articles = articles

    # Paginate regular articles (exclude featured)
    paginator = Paginator(regular_articles, 6)  # Show 6 articles per page
    # Get page number from URL query parameters
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)  # Get the requested page object

    # Check if there are any news articles
    has_news = articles.exists()

    context = {
        'featured_article': featured_article,
        'page_obj': page_obj,
        'has_news': has_news,
    }

    return render(request, 'Website/news.html', context)


def news_detail(request, slug):
    """
    News article detail page view function.
    Displays a specific article and related articles in the same category.

    Args:
        request: The HTTP request
        slug: The article slug from the URL
    """
    # Get the specific article by slug, ensuring it's published
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)

    # Get related articles (same category, excluding current)
    related_articles = NewsArticle.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:3]  # Limit to 3 related articles

    context = {
        'article': article,
        'related_articles': related_articles,
    }

    return render(request, 'Website/news-detail.html', context)


def sponsors(request):
    """
    Sponsors page view function.
    Simple view that renders the sponsors/partners page.
    """
    return render(request, 'Website/sponsors.html')


def contact(request):
    """
    Contact page view function.
    Retrieves upcoming events to display in the sidebar.
    """
    # Get upcoming events for the calendar section
    from django.utils import timezone
    upcoming_events = RaceEvent.objects.filter(
        is_active=True,
        start_date__gte=timezone.now().date()  # Only future events
    ).order_by('start_date')[:5]  # Limit to 5 upcoming events

    # Get current year for display
    current_year = timezone.now().year

    context = {
        'upcoming_events': upcoming_events,
        'current_year': current_year
    }

    return render(request, 'Website/contact.html', context)


def calendar(request):
    """
    Race calendar page view function.
    Retrieves and displays all racing events.
    Marks events as upcoming based on current date.
    """
    # Get all active events sorted by start date
    events = RaceEvent.objects.filter(is_active=True).order_by('start_date')

    # Get current date for comparison
    today = timezone.now().date()

    # Mark events as upcoming (for special display styling)
    for event in events:
        event.is_upcoming_event = event.is_upcoming  # Using model property

    # Check if there are any events
    has_events = events.exists()

    # Get current year for display
    current_year = timezone.now().year

    context = {
        'events': events,
        'has_events': has_events,
        'current_year': current_year
    }

    return render(request, 'Website/calendar.html', context)
