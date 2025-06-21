from django.contrib import admin
from .models import Station,Train,Route,Stops,Booking,Wallet,Seating,Day


class Stopin(admin.TabularInline):
    model=Stops
    extra=1
    fields=('station','arrival_time','departure_time','stop_order','fare_multiplier')



class Seatingin(admin.TabularInline): 
    model=Seating
    extra=1
    fields=('name','price_class','total_seats','available_seats','tatkal_seats')  


    
class RouteAdmin(admin.ModelAdmin):
    inlines=[Stopin]


class TrainAdmin(admin.ModelAdmin):
    inlines=[Seatingin]


admin.site.register(Train) 
admin.site.unregister(Train)  
admin.site.register(Booking)
admin.site.register(Wallet)
admin.site.register(Seating)
admin.site.register(Station)     
admin.site.register(Route,RouteAdmin)
admin.site.unregister(Seating)
admin.site.register(Train,TrainAdmin)
admin.site.register(Day) 
# Register your models here.
