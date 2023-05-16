from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser
from .models import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max
from .serializer import *
from backend import settings
from email.message import  EmailMessage
import ssl
import smtplib
import random
from datetime import datetime
import pytz
utc=pytz.UTC
def authenticateUser(email,password):
    obj=User.objects.filter(email=email)
    if len(obj)==0 :
        return False
    obj=obj[0]
    if obj.password==password:
        return True
    return False    
def evalVal(a):
    if(type(a)!=type("abcd")) :
        return a
    for i in a:
        if i!='.'  and  not (ord(i)>=48 and ord(i)<=57):
            return a
    return eval(a)
def sendMail(email_receiver,otp):
    email_sender="yourmail@gmail.com"
    email_password='yourpassword'
    subject="OTP generation"
    body="Your otp for ebid is "+str(otp)
    em=EmailMessage()
    em["From"]=email_sender
    em["To"]=email_receiver
    em['Subject']=subject
    em.set_content(body)
    context=ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())
class MakeOTPView(APIView):
    serializer_class=OTPSerializer
    def post(self,request):
        params=""
        if  "params" in request.data:
            params=request.data["params"]
        else :
            return Response(data={"can not handle this request"})
        if "email" in params:
            myemail=params["email"]
            myotp=random.randint(100000,999999)
            sendMail(myemail,myotp)
            serializer=OTP(email=myemail,otp=myotp)
            serializer.save()
            return Response(data={"right"})
        else :
            return Response(data={'wrong'})
class CreateUser(APIView):
    serializer_class=UserSerializer
    def post(self,request):
        if "params" in request.data:
            params=request.data["params"]
        else:
            return Response(data="invalid arguments")                
        if "email" in  params and "password" in params and "fName" in params and "otp" in request.data["params"]:
            myotp=request.data["params"]["otp"]
            mymail=request.data["params"]["email"]
            userObj=User.objects.filter(email=mymail)
            if(len(userObj)):
                return Response(data={"User already exist"})
            obj=OTP.objects.filter(email=mymail)

            # if(len(obj)):
            #     obj=obj[0]
            # else:
            #     return Response(data={"no otp has been sent to this email"})
            if obj.otp==myotp:
                serializer=User(email=request.data["params"]["email"],password=request.data["params"]["password"],firstName=request.data["params"]["fName"])
                serializer.save()
                return Response(data={"isAuthenticated"})
            else:
                return Response(data={"Wrong OTP"})
        return Response(data={"Invalid Request"})
    
class CreateRoomView(APIView):
    serializer_class=AuctionRoom
    def post(self,request):
        params=request.data["params"]
        if 'email' and 'password' and  'productName' and   'productDetail' and 'bidDiff' in params :
            myEmail=str(params["email"])
            myPassword=str(params["password"])
            myProductName=str(params["productName"])
            myProductDetail=str(params["productDetail"])
            myBidDiff=eval(params["bidDiff"])
            myBidDiff=1000
            
            if type(evalVal(str(myBidDiff)))==type(1):
                myBidDiff=evalVal(str(myBidDiff))
            else:
                return Response(data={"invalid Bid difference"})
            obj=User.objects.filter(email=myEmail)
            if len(obj)==0 or obj[0].password!=myPassword:
                return Response(data={"wrong User"})
            serializer=AuctionRoom(
                roomOwner=obj[0],
                productName=myProductName,
                productDetail=myProductDetail,
                bidDiff=myBidDiff,
                )
            if "upperLimit" in params and type(evalVal(params["upperLimit"]))==type(5):
                serializer.upperLimit=params["upperLimit"]
            if "lowerLimit" in params and type(evalVal(params["lowerLimit"]))==type(5):
                serializer.upperLimit=params["lowerLimit"]
            serializer.save()
            return Response(data={"room created Successfully"})
        else:
            return Response(data={"invalid Request"})
class MakeBidView(APIView):
    def post(self,request):
        if "params" in request.data:
            params=request.data["params"]
        else:
            return Response(data={"no params"})
        if  ("email" in params) and ("password" in params) and ("bidPrice" in params) and ("roomId" in params):
            myEmail=params["email"]
            myPassword=params["password"]
            myBidPrice=params["bidPrice"]
            myRoomId=params["roomId"]
            userObj=User.objects.filter(email=myEmail)
            #is user valid
            if len(userObj)==0 or userObj[0].password!=myPassword:
                return Response(data={"wrong User"})
            userObj=userObj[0]
            #is auction room valid
            roomObj=AuctionRoom.objects.filter(roomId=myRoomId)
            if len(roomObj)==0:
                return Response(data="Invalid room")
            roomObj=roomObj[0]
            #is room owner is bidding
            if(roomObj.roomOwner==userObj):
                return Response(data={"cannot bid in your own room"})
            #is it right time to bid
            now=datetime.now()
            
            startTime=roomObj.startTime.replace(tzinfo=utc)
            endTime=roomObj.endTime.replace(tzinfo=utc)
            now=now.replace(tzinfo=utc)
            if now<startTime or now>endTime:
                return Response(data={"You are either too early or too late"})    
            # is bid value correct
            maxBid=Bid.objects.filter(room=roomObj)
            if len(maxBid):
                maxBid=maxBid.aggregate(Max('bidPrice'))["bidPrice__max"]
            else:
                maxBid=roomObj.lowerLimit-roomObj.bidDiff
            if  type(evalVal(myBidPrice))!=type(4) or maxBid+roomObj.bidDiff!=evalVal(myBidPrice):
                return Response(data={"cannot bid right now"})
            serializer=Bid(user=userObj,room=roomObj,bidPrice=myBidPrice)
            serializer.save()
            return Response(data={"everything is well"})
        return Response(data="Not valid argument")
    
class GetRoomView(APIView):
    def post(self,request):

        if "params" in request.data:
            params=request.data["params"]
        else :
            return Response(data={"no params"},status=status.HTTP_400_BAD_REQUEST)
        if "roomId" in params:
            room=AuctionRoom.objects.filter(roomId=params["roomId"])
            if(len(room)):
                room=room[0]
            else :
                return Response(status=status.HTTP_400_BAD_REQUEST)
            resData={}
            resData["productName"]=room.productName
            resData["productDetail"]=room.productDetail
            resData["bidDiff"]=room.bidDiff
            resData["minBid"]=room.lowerLimit
            resData["endTime"]=room.endTime
            return Response(data=resData)
        else:
            return Response(data="No room Exists" ,status=status.HTTP_400_BAD_REQUEST)
class Top10(APIView):
    def post(self,request):
        if "params" in request.data:
            params=request.data["params"]
        else :
            return Response(data={"no params"},status=status.HTTP_400_BAD_REQUEST)
        if "roomId" in params:
            roomId=params["roomId"]
            room=AuctionRoom.objects.filter(roomId=roomId)
            if len(room)==0:
                return Response(status=status.HTTP_404_NOT_FOUND)
            room=room[0]
            obj=Bid.objects.filter(room=room).order_by('-bidPrice')
            resData=list()
            for i in range(0,min(10,len(obj))):
                temp=obj[i]
                resData.append([temp.user.firstName,temp.bidPrice])
            return Response(data=resData,status=status.HTTP_200_OK) 
        return Response(status=status.HTTP_200_OK)
class UserRooms(APIView):
    def post(self,reqeuest):
        if "params" in reqeuest.data:
            params=reqeuest.data["params"]
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "email" in params and "password" in params:
            email=params["email"]
            password=params["password"]
            if authenticateUser(email,password)!=True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            userObj=User.objects.filter(email=email)[0]
            auctionObj=AuctionRoom.objects.filter(roomOwner=userObj).order_by('-startTime')
            resData=list()
            for i in auctionObj:
                resData.append(i.productName)
            return Response(data=resData,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
class UserBids(APIView):
    def post(self,reqeuest):
        if "params" in reqeuest.data:
            params=reqeuest.data["params"]
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "email" in params and "password" in params:
            email=params["email"]
            password=params["password"]
            if authenticateUser(email,password)!=True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            userObj=User.objects.filter(email=email)[0]
            bidObj=Bid.objects.filter(user=userObj)
            resData=list()
            for i in bidObj:
                resData.append(i.room.productName)
            return Response(data=resData,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
class UserInfo(APIView):
    def post(self,reqeuest):
        if "params" in reqeuest.data:
            params=reqeuest.data["params"]
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "email" in params and "password" in params:
            email=params["email"]
            password=params["password"]
            if authenticateUser(email,password)!=True:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
