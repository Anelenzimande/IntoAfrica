from django.contrib import admin
from .models import GalleryCategory, GalleryImage
from django.utils.html import format_html
from .models import NewsCategory, NewsArticle
from .models import EventCategory, RaceEvent
from django.utils import timezone
from django.utils.html import format_html
from .models import TeamDepartment, TeamMember, TeamMemberSkill


# ----------- GALLERY REGISTER ---------

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GalleryImageInline]


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at', 'is_visible')
    list_filter = ('category', 'is_visible', 'uploaded_at')
    search_fields = ('title', 'description')
    list_editable = ('is_visible',)


# ----------- NEWS REGISTER ---------

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published',
                    'is_featured', 'is_published', 'display_image')
    list_filter = ('category', 'is_featured', 'is_published', 'date_published')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date_published'
    list_editable = ('is_featured', 'is_published')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'excerpt', 'content')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Publication', {
            'fields': ('date_published', 'is_featured', 'is_published')
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="auto" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'


# ----------- CALENDAR REGISTER -------------


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(RaceEvent)
class RaceEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'location', 'date_display',
                    'round_display', 'category', 'is_active', 'upcoming_status')
    list_filter = ('category', 'is_active', 'start_date')
    search_fields = ('title', 'venue', 'location', 'description')
    date_hierarchy = 'start_date'
    list_editable = ('is_active',)

    fieldsets = (
        (None, {
            'fields': ('title', 'venue', 'location', 'category')
        }),
        ('Event Details', {
            'fields': ('start_date', 'end_date', 'round_number', 'championship', 'description')
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )

    def date_display(self, obj):
        if obj.end_date:
            return f"{obj.get_month_display} {obj.start_date.day}-{obj.end_date.day}"
        return f"{obj.get_month_display} {obj.start_date.day}"
    date_display.short_description = 'Date'

    def round_display(self, obj):
        if obj.round_number:
            return f"Round {obj.round_number}"
        return "-"
    round_display.short_description = 'Round'

    def upcoming_status(self, obj):
        if obj.is_upcoming:
            return True
        return False
    upcoming_status.boolean = True
    upcoming_status.short_description = 'Upcoming'

# ----------- TEAM MEMBERS -------------


class TeamMemberSkillInline(admin.TabularInline):
    model = TeamMemberSkill
    extra = 1


@admin.register(TeamDepartment)
class TeamDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'department',
                    'display_order', 'is_active', 'display_photo')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'role', 'bio')
    list_editable = ('display_order', 'is_active')
    inlines = [TeamMemberSkillInline]

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="auto" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = 'Photo'
