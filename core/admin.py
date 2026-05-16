from django.contrib import admin
from .models import Category, Cluster, Course, UpcomingEvent, Testimonial, Payment, FeedBack, CourseRegistration, AccessModel
# Register your models here.

class ClusterInline(admin.TabularInline):
    model  = Cluster
    extra  = 0
    fields = ('order', 'slug', 'label', 'color')


class CourseInline(admin.TabularInline):
    model              = Course
    extra              = 0
    fields             = ('rank_id', 'num', 'title', 'level', 'duration', 'price', 'cluster')
    show_change_link   = True


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'short', 'color', 'badge', 'bespoke', 'course_count', 'order')
    search_fields = ('name',)
    list_editable = ('order',)
    ordering = ('order', 'name')
    inlines = [ClusterInline, CourseInline]
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Courses'


class ClusterAdmin(admin.ModelAdmin):
    list_display  = ('category', 'order', 'slug', 'label', 'color')
    list_filter   = ('category',)
    list_editable = ('order',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('rank_id', 'num', 'title', 'category', 'cluster', 'level', 'duration', 'price', 'is_popular')
    list_filter = ('category', 'cluster', 'training_format', 'is_popular')
    search_fields = ('title', 'subtitle', 'teaser', 'description')
    ordering = ('rank_id', 'title')
    
    fieldsets = (
        ('Identity',    {'fields': ('rank_id', 'num', 'title', 'subtitle', 'category', 'cluster')}),
        ('Content',     {'fields': ('teaser', 'description', 'audience', 'objectives', 'outlines', 'goals')}),
        ('Delivery',    {'fields': ('duration', 'level', 'price', 'training_format', 'mode')}),
        ('Flags',       {'fields': ('is_popular', 'is_upcoming', 'url', 'image')}),
    )

class UpcomingEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'dates', 'location', 'expires')
    fieldsets = (
        ('Core',        {'fields': ('slug', 'title', 'subtitle', 'partners', 'dates', 'location', 'expires')}),
        ('Detail',      {'fields': ('sectors', 'stats', 'body')}),
        ('Facilitator', {'fields': ('facilitator_label', 'facilitator_name', 'facilitator_bio')}),
    )

class TestimonialsAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'author_title')
    search_fields = ('author_name',)
    ordering = ('author_name',)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('get_customer', 'get_customer_email', 'get_customer_phone_number', 'amount', 'status')
    search_fields = ('get_customer', 'get_customer_email', 'get_customer_phone_number', 'amount',)
    ordering = ('-created_at',)
    
    def get_customer_email(self, obj):
        return obj.customer.email if obj.customer else 'N/A'
    
    def get_customer_phone_number(self, obj):
        return obj.customer.phone_number if obj.customer else 'N/A'

    def get_customer(self, obj):
        return obj.customer if obj.customer else 'N/A'



class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    ordering = ('-created_at',)



class AccessModelAdmin(admin.ModelAdmin):
    list_display = ("id",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Cluster, ClusterAdmin)
admin.site.register(Testimonial, TestimonialsAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(FeedBack)
admin.site.register(CourseRegistration)



admin.site.site_header = 'Citadel Admin'
admin.site.site_title = 'Citadel Admin Portal'
admin.site.index_title = 'Welcome to Citadel Admin Portal'




class AdminSetUp(admin.AdminSite):
    site_header = 'Citadel Admin'
    site_title = 'Citadel Admin Portal'
    index_title = 'Welcome to Citadel Admin Portal'
    

admin_set_up = AdminSetUp(name='dev-admin')
admin_set_up.register(Category, CategoryAdmin)
admin_set_up.register(Course, CourseAdmin)  
admin_set_up.register(Testimonial, TestimonialsAdmin)
admin_set_up.register(Payment, PaymentAdmin)
admin_set_up.register(FeedBack)
admin_set_up.register(CourseRegistration)
admin_set_up.register(AccessModel, AccessModelAdmin)
