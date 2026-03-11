from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Property, PropertyType, PropertyApplication
from .forms import PropertyApplicationForm, PropertySearchForm


def property_list(request):
    """Display list of all properties with filtering"""
    properties = Property.objects.filter(is_active=True)
    form = PropertySearchForm(request.GET)
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            properties = properties.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search) |
                Q(address__icontains=search) |
                Q(state__icontains=search)
            )
        
        transaction_type = form.cleaned_data.get('transaction_type')
        if transaction_type:
            properties = properties.filter(
                Q(transaction_type=transaction_type) | Q(transaction_type='both')
            )
        
        status = form.cleaned_data.get('status')
        if status:
            properties = properties.filter(status=status)
        
        min_price = form.cleaned_data.get('min_price')
        if min_price:
            properties = properties.filter(price__gte=min_price)
        
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            properties = properties.filter(price__lte=max_price)
        
        min_bedrooms = form.cleaned_data.get('min_bedrooms')
        if min_bedrooms:
            properties = properties.filter(bedrooms__gte=min_bedrooms)
        
        city = form.cleaned_data.get('city')
        if city:
            properties = properties.filter(city__icontains=city)
    
    # Featured properties
    featured_properties = Property.objects.filter(is_active=True, is_featured=True)[:6]
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'featured_properties': featured_properties,
        'form': form,
        'total_count': properties.count(),
    }
    return render(request, 'realestate/property_list.html', context)


def property_detail(request, slug):
    """Display single property detail"""
    property_obj = get_object_or_404(Property, slug=slug, is_active=True)
    
    # Increment views
    property_obj.increment_views()
    
    # Get related properties (same type or city)
    related_properties = Property.objects.filter(
        Q(property_type=property_obj.property_type) | Q(city=property_obj.city),
        is_active=True
    ).exclude(id=property_obj.id)[:4]
    
    # Application form
    if request.method == 'POST':
        form = PropertyApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.property = property_obj
            if request.user.is_authenticated:
                application.user = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully! We will contact you soon.')
            return redirect('realestate:property_detail', slug=slug)
    else:
        # Pre-fill form if user is authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'phone': request.user.contact_no if hasattr(request.user, 'contact_no') else '',
            }
        form = PropertyApplicationForm(initial=initial_data)
    
    context = {
        'property': property_obj,
        'related_properties': related_properties,
        'form': form,
        'images': property_obj.images.all(),
    }
    return render(request, 'realestate/property_detail.html', context)


def property_by_type(request, type_name):
    """Display properties filtered by type"""
    property_type = get_object_or_404(PropertyType, name__iexact=type_name)
    properties = Property.objects.filter(property_type=property_type, is_active=True)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'property_type': property_type,
        'total_count': properties.count(),
    }
    return render(request, 'realestate/property_by_type.html', context)


def my_applications(request):
    """Display user's property applications (requires authentication)"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view your applications.')
        return redirect('accounts:login')
    
    applications = PropertyApplication.objects.filter(user=request.user).select_related('property')
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'applications': page_obj,
    }
    return render(request, 'realestate/my_applications.html', context)


def application_detail(request, pk):
    """Display single application detail"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view this application.')
        return redirect('accounts:login')
    
    application = get_object_or_404(
        PropertyApplication, 
        pk=pk, 
        user=request.user
    )
    
    context = {
        'application': application,
    }
    return render(request, 'realestate/application_detail.html', context)