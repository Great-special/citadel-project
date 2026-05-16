from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify



class Category(models.Model):
    """One per track (Track 1: Leadership Journey, etc.)."""
    order    = models.PositiveIntegerField(_('order'), default=0,
                   help_text="Display order — lowest first")
    name     = models.CharField(_('name'), max_length=100,
                   help_text="Full label e.g. 'Track 1: Leadership Journey'")
    short    = models.CharField(_('short label'), max_length=60, blank=True,
                   help_text="Breadcrumb label e.g. 'Leadership Journey'")
    slug     = models.SlugField(_('slug'), max_length=100, blank=True, null=True, unique=True)
    color    = models.CharField(_('accent colour'), max_length=20, default='#C8960C',
                   help_text="Hex colour used for the track tab and cards")
    badge    = models.CharField(_('badge'), max_length=20, blank=True,
                   help_text="Optional badge text e.g. 'NEW'")
    faculty  = models.CharField(_('faculty line'), max_length=500, blank=True,
                   help_text="Faculty credit line shown below the track header")
    bespoke  = models.BooleanField(_('bespoke track'), default=False,
                   help_text="Marks this as the bespoke / in-house track")
    image    = models.ImageField(_('image'), upload_to='category_images/', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name        = _('track / category')
        verbose_name_plural = _('tracks / categories')
        ordering            = ['order', 'id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip()
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Cluster(models.Model):
    """
    Sub-track grouping within a Category.
    uses clusters — AIM, Offshore, OFC, ASME.
    Other tracks simply have no Cluster rows.
    """
    category = models.ForeignKey(
        Category, verbose_name=_('track'),
        on_delete=models.CASCADE, related_name='clusters'
    )
    slug  = models.SlugField(_('slug'), max_length=50,
                help_text="Short identifier e.g. 'aim', 'asme', 'ofc'")
    label = models.CharField(_('label'), max_length=100,
                help_text="Display name e.g. 'Asset Integrity Management'")
    color = models.CharField(_('colour'), max_length=20, blank=True,
                help_text="Override hex colour; falls back to the track colour")
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name        = _('cluster / sub-track')
        verbose_name_plural = _('clusters / sub-tracks')
        ordering            = ['order', 'id']
        unique_together     = [['category', 'slug']]

    def __str__(self):
        return f"{self.category.name} › {self.label}"


class Course(models.Model):
    rank_id  = models.IntegerField(_('order'), blank=True, null=True,
                   help_text="Controls display order within the track — lower = first")
    num      = models.CharField(_('course number / code'), max_length=100, blank=True,
                   help_text="e.g. '01 Leadership Journey' or 'AIM 01'")
    title    = models.CharField(_('title'), max_length=255)
    subtitle = models.CharField(_('subtitle'), max_length=255, blank=True)

    # 'description' stores the synopsis (detail-page body).
    # 'teaser' is the ~30-word card preview.
    description = models.TextField(_('synopsis'),
                      help_text="Full body text shown on the detail page")
    teaser      = models.TextField(_('teaser'), blank=True,
                      help_text="~30-word card preview shown in the programme grid")
    audience    = models.TextField(_('who should attend'), blank=True)

    objectives  = models.TextField(_('objectives'), blank=True, null=True,
                      help_text="Comma-separated e.g.: Understand X, Develop Y")
    outlines    = models.TextField(_('outlines'), blank=True, null=True,
                      help_text="Module:Topic, Module:Topic format")
    goals       = models.TextField(_('goals'), blank=True, null=True,
                      help_text="Comma-separated goals")
    image       = models.ImageField(_('image'), upload_to='course_images/', null=True, blank=True)

    price    = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    duration = models.CharField(_('duration'), max_length=50)
    level    = models.CharField(_('level'), max_length=100, blank=True,
                   help_text="e.g. 'Advanced', 'Senior Leaders', 'All Leaders'")

    category = models.ForeignKey(
        Category, verbose_name=_('track'),
        on_delete=models.CASCADE, related_name='courses'
    )
    cluster  = models.ForeignKey(
        Cluster, verbose_name=_('cluster'),
        on_delete=models.SET_NULL, null=True, blank=True, related_name='courses'
    )
    mode             = models.CharField(_('mode'), max_length=150, blank=True, null=True)
    training_format  = models.CharField(
        _('training format'), max_length=150,
        choices=(
            ('Online',    'Online'),
            ('Classroom', 'Classroom'),
            ('Executive', 'Executive'),
            ('Bespoke',   'Bespoke'),
        ),
        default='Online'
    )
    url         = models.URLField(_('url'), null=True, blank=True)
    is_popular  = models.BooleanField(_('is popular'), default=False)
    is_upcoming = models.BooleanField(_('is upcoming'), default=False)
    created_at  = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name        = _('course')
        verbose_name_plural = _('courses')
        ordering            = ['category__order', 'rank_id', 'id']

    def __str__(self):
        return self.title

    @property
    def fee_display(self):
        if self.price is None:
            return '€3,999'
        return f'€{int(self.price):,}'


class UpcomingEvent(models.Model):
    slug      = models.SlugField(_('slug'), max_length=100, unique=True,
                    help_text="e.g. 'soe-governance-2026'")
    title     = models.CharField(_('title'), max_length=300)
    subtitle  = models.TextField(_('subtitle'), blank=True)
    partners  = models.CharField(_('partners'), max_length=300, blank=True)
    dates     = models.CharField(_('dates (display string)'), max_length=100,
                    help_text="e.g. '1 – 4 September 2026'")
    location  = models.CharField(_('location'), max_length=200)
    expires   = models.DateField(_('auto-expiry date'), null=True, blank=True,
                    help_text="Banner is hidden on and after this date")
    sectors   = models.JSONField(_('sectors'), default=list, blank=True,
                    help_text='JSON list e.g. ["Energy", "Finance"]')
    stats     = models.JSONField(_('stats'), default=list, blank=True,
                    help_text='JSON list e.g. [{"n": "3.5", "l": "Intensive Days"}]')
    body      = models.TextField(_('body copy'), blank=True)

    # Facilitator — flat fields, no need for a sub-model
    facilitator_label = models.CharField(_('facilitator label'), max_length=100,
                            default='Lead Facilitator', blank=True)
    facilitator_name  = models.CharField(_('facilitator name'), max_length=200, blank=True)
    facilitator_bio   = models.TextField(_('facilitator bio'), blank=True)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name        = _('upcoming event')
        verbose_name_plural = _('upcoming events')
        ordering            = ['expires']

    def __str__(self):
        return self.title


class Testimonial(models.Model):  # Changed from plural to singular
    author_name = models.CharField(_('author name'), max_length=100)
    author_title = models.CharField(_('author title'), max_length=100, null=True, blank=True)
    author_image = models.ImageField(_('author image'), upload_to='testimonials/', null=True, blank=True)
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('testimonial')
        verbose_name_plural = _('testimonials')

    def __str__(self):
        return self.author_name


class EnrolledCustomer(models.Model):
    customer = models.CharField(max_length=255, verbose_name=_('customer'))
    email = models.EmailField(_('Email'))
    phone_number = models.CharField(_('Phone Number'), max_length=25, blank=True, null=True)
    city = models.CharField(_('City'), max_length=100)
    country = models.CharField(_('Country'), max_length=100)
    postcode = models.CharField(_('Postcode'), max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('Course'), related_name='courses')

    class Meta:
        verbose_name = _('enrolled_customer')
        verbose_name_plural = _('enrolled_customers')
    
    def __str__(self):
        return f"{self.customer} ({self.course.title})"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
    ]
    
    customer = models.ForeignKey(EnrolledCustomer, on_delete=models.CASCADE, verbose_name=_('Customer'), related_name='customers')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('amount'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('currency'))
    quantity = models.IntegerField(_('Quantity'))
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_('status'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='', verbose_name=_('payment method'))
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, verbose_name=_('stripe payment intent id'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at')) 
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
    
    def __str__(self):
        return f"{self.amount} {self.currency}"
    
class FeedBack(models.Model):
    name = models.CharField(max_length=125, verbose_name=_('name'))
    email = models.EmailField(verbose_name=_('email'))
    message = models.TextField(verbose_name=_('message'))
    status = models.CharField(max_length=50, verbose_name=('status'), choices=(('Pending', 'Pending'), ('Attended', 'Attended')), default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name} ({self.email})"
    
    
class CourseRegistration(models.Model):
    TITLE_CHOICES = [("Mr.", "Mr."), ("Mrs.", "Mrs."), ("Ms.", "Ms."), ("Dr.", "Dr.")]
    
    session = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='registrations', verbose_name=_('course'))
    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    designation = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class AccessModel(models.Model):
    mode = models.CharField(max_length=50, verbose_name=_('mode'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description'))
    allowed = models.BooleanField(default=True, verbose_name=_('allowed'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    
    def __str__(self):
        return self.mode
    