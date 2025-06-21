from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone


class Station(models.Model):
    name=models.CharField(max_length=50)
    code=models.CharField(max_length=4,null=True,blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


    def __str__(self):
        return (f'Station:{self.name} ID:{self.code}')



class Day(models.Model):
    DAY_CHOICES = [
        ("Monday","Monday"),
        ("Tuesday","Tuesday"),
        ("Wednesday","Wednesday"),
        ("Thursday","Thursday"),
        ("Friday","Friday"),
        ("Saturday","Saturday"),
        ("Sunday","Sunday")
    ]
    day_running= models.CharField(
        max_length=20,
        unique=True,
        choices=DAY_CHOICES,
    )   

    def __str__(self):
        return dict(self.DAY_CHOICES).get(self.day_running, self.day_running)


class Train(models.Model):
    name=models.CharField(max_length=50)
    number=models.IntegerField()
    base_fare=models.DecimalField(max_digits=4, decimal_places=2)


    def __str__(self):
        return(f'{self.name}')


   

class Route(models.Model):
    train=models.ForeignKey(Train, related_name='rout',on_delete=models.CASCADE)
    day=models.ManyToManyField(Day)


    def __str__(self):
     return (f'{self.train}')



class Stops(models.Model):
    route=models.ForeignKey(Route,related_name='st',on_delete=models.CASCADE)
    station=models.ForeignKey(Station,on_delete=models.CASCADE,default=1)
    stop_order = models.PositiveIntegerField()  
    arrival_time = models.TimeField(blank=True,null=True) 
    departure_time= models.TimeField(blank=True,null=True)
    fare_multiplier=models.DecimalField(max_digits=5,decimal_places=4,default=0.0) 


    class Meta:
        ordering = ['stop_order']
        unique_together = [['route', 'stop_order']]



    def __str__(self):
        return (str(int(self.stop_order))) 


class Seating(models.Model):
    train=models.ForeignKey(Train, related_name='seats',on_delete=models.CASCADE)
    day=models.ManyToManyField(Day)
    name = models.CharField(max_length=50)  
    price_class = models.DecimalField(max_digits=5, decimal_places=2)
    total_seats=models.IntegerField(default=0)
    available_seats = models.IntegerField(default=0)
    tatkal_seats=models.IntegerField(default=0)


    def __str__(self):
     return (f'Train:{self.train} Class:{self.name} Available seats:{self.available_seats}')






class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    passenger_name=models.CharField(max_length=100)
    passenger_email=models.EmailField(max_length=100)
    booking_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=30, choices=[('booked', 'Booked'), ('cancelled', 'Cancelled'),('Waitlisted','waitlisted'),('Payment_pending','Payment_pending')], default='booked')
    boarding=models.CharField(max_length=100)
    deboarding=models.CharField(max_length=100)
    travelling_class=models.CharField(max_length=100,default='none')
    cost=models.IntegerField(default='0')
    deboarding_stop=models.IntegerField(default='0')
    journey_date=models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.train.name} ({self.num_tickets} tickets)"

    def cancel_booking(self):
        if self.status == 'cancelled':
            raise ValueError("This booking has already been cancelled.")
        self.status = 'cancelled'
        self.save()



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"




class Search_results(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True,null=True,blank=True)
    train_name=models.CharField(max_length=20) 
    train_id=models.IntegerField(default=0,null=True,blank=True)
    boarding=models.CharField(max_length=100)
    deboarding=models.CharField(max_length=100)
    deboarding_stop=models.IntegerField(default='0')
    arrival_time=models.TimeField()
    departure_time= models.TimeField()
    seat_class=models.CharField(max_length=20,null=True,blank=True)
    fare_diff=models.DecimalField(max_digits=5, decimal_places=2,default='0')
    num_ticket=models.IntegerField(default=0)
    journey_date=models.DateField(default=timezone.now)


    def __str__(self):
        return (f'{self.train_name}')


class Temp_seat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,db_index=True)
    name = models.CharField(max_length=50)
    seats=models.IntegerField()
    price=models.DecimalField(max_digits=5, decimal_places=2,default='0')
    









# Create your models here.
