import Graph_Auth as auth
x=auth.GraphAuth()
if x == True:
#the rest of your code is here if the user is identified
    print("Access Granted")
elif x==5:
    exit
elif x==404:
    print("You are locked out.")
else:
    exit
