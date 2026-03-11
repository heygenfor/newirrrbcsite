import csv
from datetime import date
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    filename = f"data_export_{date.today()}.csv"  # Include the current date in the filename
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    model = queryset.model
    fields = [field.name for field in model._meta.fields]

    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])

    return response

export_as_csv.short_description = "Export selected objects as CSV"
