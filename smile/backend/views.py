from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login,authenticate  
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib import admin
from .forms import Searchform,Bookingform
from django.forms import formset_factory
from .models import Day,Station,Train,Route,Stops,Seating,Wallet,Search_results,Temp_seat,Booking
from django.db.models import Q,F,Subquery, OuterRef,Count,Sum
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

def home(request):
    if request.method=="POST":
        username=request.POST.get('username')
        pas=request.POST.get('password')
        u=User.objects.filter(username=username)
        user=authenticate(request,username=username,password=pas)
        if user is not None:
            login(request,user)
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            print(wallet.balance)
            return render(request,"backend/dashboard.html",{"w":wallet})
        else:
            return render(request,"backend/login.html",{"error":"wrong username or password"})

    else:
        return render(request,"backend/login.html")    


def register(request):
    if request.method=="POST":
        username=request.POST.get('username')
        pas=request.POST.get('password')
        re_pas=request.POST.get('confirm_password')
        print(f"\n {pas}. {re_pas}\n")
        if User.objects.filter(username=username).exists():
            return render(request,"backend/register.html",{"error":"Username already taken"})
        if pas!=re_pas:
            return render(request,"backend/register.html",{"error":"Passwords don't match"})
        user=User.objects.create_user(username=username,password=pas)   
        user.save()     
        user.is_staff=True
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        return render(request,"backend/login.html",{"message":"Account successfully created !!"})

    else:
        return render(request,"backend/register.html")   


@login_required
def dasboard(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request,"backend/dashboard.html",{"w":wallet})
    

@login_required 
def search(request):
    if request.method == 'GET':
        form = Searchform(request.GET)
        if form.is_valid():
            sor=form.cleaned_data['origin']
            dest=form.cleaned_data['destination']
            date=form.cleaned_data['date']
            day_name = date.strftime("%A") 
            trains = Train.objects.filter(
            Q(rout__st__station__code=sor.code),Q(rout__day__day_running__in=day_name))
            trains1 = Train.objects.filter(
            Q(rout__st__station__code=dest.code),Q(rout__day__day_running__in=day_name))
            common_trains = trains.filter(id__in=trains1.values('id'))
            Search_results.objects.filter(user=request.user).delete()
            for t in common_trains:
                r1=t.rout.filter(st__station__code=sor.code)
                r2=t.rout.filter(st__station__code=dest.code)
                origin_stop = Stops.objects.filter(station__code=sor.code).filter(route__id__in=r1.values('id'))
                dest_stop = Stops.objects.filter(station__code=dest.code).filter(route__id__in=r2.values('id'))
                if origin_stop.exists() and dest_stop.exists():
                    if origin_stop.first().stop_order>dest_stop.first().stop_order:
                        common_trains= common_trains.exclude(number=t.number)
                    else:
                        obj=Search_results.objects.create(
                            user=request.user,
                            train_name=t.name,
                            boarding=sor.name,
                            deboarding=dest.name,
                            arrival_time=origin_stop.first().departure_time,
                            departure_time=dest_stop.first().arrival_time,
                            deboarding_stop=origin_stop.first().stop_order,
                            fare_diff=(origin_stop.first().fare_multiplier-dest_stop.first().fare_multiplier)*t.base_fare,
                            train_id=t.id,
                            journey_date=date
                        )   
                        obj.save() 
            train_info=Search_results.objects.all().distinct()          
            return render(request,"backend/search_results.html",{'train':train_info})
    else:
        form = Searchform()
        return render(request,"backend/search.html",{"form":form})


@login_required
def select_class(request,t_id):
    if request.method == 'GET':
        print(f"\nt_id:{t_id}\n")
        train=Train.objects.get(id=t_id)
        train_info=Search_results.objects.get(train_id=t_id)
        Search_results.objects.filter(user=request.user).exclude(train_id=t_id).delete()
        Temp_seat.objects.filter(user=request.user).delete()
        for t in train.seats.all():
            fare=t.price_class*train_info.fare_diff
            booked_seats = (Booking.objects.filter(status='booked',train__id=t_id,deboarding_stop__gte=train_info.deboarding_stop,journey_date=train_info.journey_date)).count()
            obj=Temp_seat.objects.create(user=request.user,name=t.name,price=fare,seats=t.available_seats-booked_seats)
            obj.save()
        seat_info=Temp_seat.objects.all().distinct()
        print(seat_info)
        return render(request,"backend/select_class.html",{'seats':seat_info}) 
    else:
        return render(request,"backend/select_class.html")  


@login_required
def book_ticket(request,query):
    if request.method=="POST":
        num=int(request.POST.get('number'))
        return redirect('book',num=num,query=query)
    else:
        return render(request,"backend/book_ticket.html")    


@login_required
@transaction.atomic
def book(request,num,query):
    if request.method=="POST":
        train_info=Search_results.objects.get(user=request.user)
        form=formset_factory(Bookingform,extra=num)
        seat_info=Temp_seat.objects.get(name=query)
        formset = form(request.POST)
        train=Train.objects.get(id=train_info.train_id)
        cost=num*seat_info.price 
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        if(cost>wallet.balance):
            return HttpResponse("You dont have enough money in the wallet required:"+str(cost)+"Current Wallet Balance: "+str(wallet.balance))
        wallet.withdraw(cost)    
        if formset.is_valid():
            for form in formset:
                name = form.cleaned_data.get('name')
                email = form.cleaned_data.get('email')
                obj=Booking.objects.create(
                    user=request.user,
                    train=train,
                    passenger_name=name,
                    passenger_email=email,
                    boarding=train_info.boarding,
                    deboarding=train_info.deboarding,
                    status='booked',
                    cost=seat_info.price,
                    deboarding_stop=train_info.deboarding_stop,
                    travelling_class=seat_info.name,
                    journey_date=train_info.journey_date
                )
                obj.save()
                Temp_seat.objects.filter(user=request.user).delete()
                Search_results.objects.filter(user=request.user).delete()  
            return render(request,"backend/confirmation.html",{"message":"Booking sucess !!","cost":cost})

    else:
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        seat_info=Temp_seat.objects.get(name=query)
        cost=num*seat_info.price 
        train_info=Search_results.objects.get(user=request.user)
        form=formset_factory(Bookingform,extra=num)
        return render(request,"backend/book.html",{"formset":form,"num":num,"query":query,"w":wallet,"cost":cost,"train":train_info})    


@login_required
@transaction.atomic
def add_money(request):
    if request.method=='POST':
        money=request.POST.get('money')
        print(money)
        if money:
            try:
                money_decimal = Decimal(money.strip())
                wallet, created = Wallet.objects.get_or_create(user=request.user)
                if(money_decimal>0):
                 wallet.deposit(money_decimal)
                 print(f"update balance is:{wallet.balance}")
                 return render(request, 'backend/dashboard.html',{'w':wallet})
                else:
                    
                 error_message = "Invalid amount entered. Please enter a valid number."
                 return render(request, 'backend/add_money.html', {'error': error_message})

            except :
                error_message = "Invalid amount entered. Please enter a valid number."
                return render(request, 'backend/add_money.html', {'error': error_message})
        else:
            error_message = "Please enter a valid amount."
            return render(request, 'backend/add_money.html', {'error': error_message})
    return render(request, 'backend/add_money.html')

            
@login_required
def bookings(request):
    booked=Booking.objects.filter(user=request.user)
    return render(request,"backend/bookings.html",{"booking":booked})


@login_required
@transaction.atomic
def cancel(request):
    booked=Booking.objects.filter(user=request.user).filter(journey_date__gt=timezone.now().date()).filter(status='booked')
    if request.method=="POST":
        ticket_ids = request.POST.getlist('ticket_ids')
        if not ticket_ids:
            return render(request,"backend/cancel.html",{"booking":booked,"error":"No tickets have been selected"})    
        refund_amount = Booking.objects.filter(
            id__in=ticket_ids,
            user=request.user,
            status='booked'
         ).aggregate(
            total_cost=Sum('cost'))
        print(refund_amount['total_cost'])
        Booking.objects.filter(
            id__in=ticket_ids,
            user=request.user  
        ).update(status='cancelled')
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.deposit(refund_amount['total_cost'])
        return render(request,"backend/dashboard.html",{"refund":refund_amount['total_cost'],"w":wallet}) 
    else:
        return render(request,"backend/cancel.html",{"booking":booked})    

    




