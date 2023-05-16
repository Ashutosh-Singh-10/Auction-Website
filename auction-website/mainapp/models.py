from django.db import models
import random
def roomIdGeneration():
    a=random.randint(10000000,99999999)
    while(len(AuctionRoom.objects.filter(roomId=a))):
        a=random.randint(10000000,99999999)
    return a
    
def randomUserIdGeneration():
    a=random.randint(10000000,99999999)
    while(len(User.objects.filter(userId=a))):
        a=random.randint(10000000,99999999)
    return a    
class User(models.Model):
    email=models.EmailField( max_length=254,blank=False,null=False,unique=True)
    userId=models.CharField( max_length=254,default=randomUserIdGeneration,primary_key=True)
    password=models.CharField(max_length=50,null=False,blank=False)
    firstName=models.CharField( max_length=30,null=False,blank=False)
    lastName=models.CharField( max_length=30,null=True,blank=True)
    userPhoto=models.ImageField( upload_to='profilePic/',null=True)
    address=models.CharField( max_length=100,null=True,blank=True)
class OTP(models.Model):
    email=models.CharField( max_length=100,null=False,blank=False,primary_key=True)
    otp=models.CharField( max_length=6,null=False,blank=False)
    time=models.DateTimeField(null=False,blank=False,auto_now=True)
class AuctionRoom(models.Model):
    productName=models.CharField(max_length=50)
    productDetail=models.CharField(max_length=150)
    productPhoto=models.ImageField( upload_to='auctionItemPic/', height_field=None, width_field=None,null=True)
    roomOwner=models.ForeignKey(User,on_delete=models.CASCADE)
    roomId=models.CharField(max_length=8,default=roomIdGeneration,primary_key=True)
    startTime=models.DateTimeField(auto_now_add=True)
    endTime=models.DateTimeField(null=True)
    bidDiff=models.IntegerField(default=500)
    upperLimit=models.IntegerField(default=1000000)
    lowerLimit=models.IntegerField(default= 0)
class Bid(models.Model):
    room=models.ForeignKey(AuctionRoom, on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    bidPrice=models.IntegerField(null=False)
    