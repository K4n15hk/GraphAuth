import warnings
warnings.filterwarnings("ignore")
import os
import sqlite3
import random
from tkinter import *
from tkinter import filedialog
from PIL import Image,ImageTk
import hashlib
import sys
import shutil
n_img=9
valid_images_list=list()
checked=False
seq_list=[]
loc=[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]]
hash_value=0
usr_identified=False
sign_up_run=False#this variable checks if the sign_up function was run or not
sign_up_seq_run_check=False
#we need to make a cache folder for this app ,it stores the last users images fetched from the database
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'cache')
if not os.path.exists(final_directory):
   os.makedirs(final_directory)
##
#this function checks if the database exists
def ifdbexists(filename):
    try:
        conn_query='file:'+filename+'?mode=r0'
        db_conn=sqlite3.connect(f"file:{filename}?mode=ro",uri =True)
        db_conn.close()
        return True
    except:
        return False    

#this function checks if the file is an imagefile and if it is then it gives
#the bit depth of that image file
def bit_depth(filename):
#dictionary containing the different modes of an image file
    mode_to_bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB": 24, "HSV": 24, "I": 32, "F": 32}
    try:
        data = Image.open(filename)
        bpp = mode_to_bpp[data.mode]
        return bpp
    except:
        return False

#this function gets the lsbs from the input file
#this function does not get all the lsbs of all bytes
#it traverses the image in chunks of size 'jump'
#and gets the lsbs of the first byte of the chunk
#it returns an integer
def getlsbhash(filename,key):
    with open(filename,'rb') as file:
        data=file.read()
        file.seek(0,os.SEEK_END)
        file_size=file.tell()
        file.seek(0,0)
        lsb=b''
        jump=900000
        iterations=int(file_size / jump)
        intlsb=0
        for iterate in range(iterations):
            byte=data[iterate * jump]
            if byte & 1:
                lsb=lsb+b'1'
            else:
               lsb = lsb+b'0'
        intlsb=int.from_bytes(lsb)
        intlsb=(intlsb+key)^69
        lsb1=int.from_bytes(hashlib.sha256(str(intlsb).encode('utf-8')).digest(), 'big')
    return lsb1

#this is the function that allows the user to sign_up to our database
def sign_up_app():
    global sign_up_run
    global sign_up_seq_run_check
    sign_up_run=True
#this class creates an object that is used for getting the images from the user         
    class GetUserImage:
        checker=False
        filename=""
        def __init__(self,root,col,ro,num,db_cursor,db_username):
            self.input_text="Select img_"+str(num)
            self.select_file=Button(root,text=self.input_text,command=self.browseFiles)
            self.select_file.grid(column=col,row=ro)
            self.usr_input_lb=Label(root,text="Empty",width=60,height=1)
            self.usr_input_lb.grid(column=col+1,row=ro)
            self.usr_input_btn=Button(root,text="Submit",command=self.get_usr_img)
            self.usr_input_btn.grid(column=col+2,row=ro)
            self.lb1=Label(root,text="Empty")
            self.lb1.grid(column=col+3,row=ro)
            self.cursor=db_cursor
            self.id=num
            self.usr_name=db_username

# Function for opening the file explorer window
        def browseFiles(self):
          self.filename = filedialog.askopenfilename(
              initialdir="/",
              title="Select a File",
              filetypes=(("All files", "*.*"),)
          )
          self.usr_input_lb.config(text=self.filename)
#this function updates the image uploaded by the user to the database and the label accordingly 
        def get_usr_img(self):
            img_path=self.filename
            if bit_depth(img_path):
                with open(img_path,'rb') as file:
                    img_data=file.read()
                query="UPDATE USERDB set img_"+str(self.id+1)+"=? WHERE Username=?"
                self.cursor.execute(query,(img_data,self.usr_name))
                if self.id not in valid_images_list:
                    valid_images_list.append(self.id)
                if len(valid_images_list) == n_img:
                    self.checker=True
                self.lb1.config(text="Done",fg='green')
            else:
                if self.id in valid_images_list:
                    valid_images_list.remove(self.id)
                self.checker=False
                self.lb1.config(text="Invalid",fg='red')
#this class creates an object to get the username 
    class GetUserName:
        usr_name=""
        check=False
        def __init__(self,root,col,ro,db_cursor):
            self.alert_text="Enter Valid Username:"
            self.lb=Label(root,text=self.alert_text)
            self.lb.grid(column=col,row=ro)
            self.input_field=Entry(root)
            self.input_field.grid(column=col+1,row=ro)
            self.input_btn=Button(root,text="Submit",command=self.get_usr_name)
            self.input_btn.grid(column=col+2,row=ro)
            self.lb1=Label(root,text="Empty")
            self.lb1.grid(column=col+3,row=ro)
            self.cursor=db_cursor
#this function checks if the username entered is valid or not 
        def get_usr_name(self):
            input_name=self.input_field.get()
            self.usr_name=input_name
            if " " in input_name:
                self.lb1.config(text="Invalid",fg='red')
            elif input_name == "":
                self.lb1.config(text="Invalid",fg='red')
            else:
#here we check if the username already exists in the database or not
                cursor.execute("SELECT Username FROM USERDB WHERE Username=?",(self.usr_name,))
                if not cursor.fetchall():    
                    query="INSERT INTO USERDB(Username,tries) VALUES(?,?)"
                    self.cursor.execute(query,(input_name,0))
                    self.check = True
                    self.lb1.config(text="Done",fg='green')
                    root.destroy()
                else:
                    self.check=False
                    root.destroy()

#this function is used to submit the 9 images if they are uploaded appropriately and changes the value of the checked
#variable 
    def submit():
        global checked
        if len(valid_images_list) == n_img:
            checked=True
            root.destroy()

#this class creates an object that is an image button with certain properties that contain a user image
    class img_button(Button):
        btn_id=0
        check=False
        def __init__(self,root,image_name,col,ro,button_id):
            self.photo=Image.open(image_name)
            self.resized=self.photo.resize((150,150),Image.LANCZOS)
            self.img=ImageTk.PhotoImage(self.resized)
            Button.__init__(self,master=root,image=self.img,text=" ",bg='red',compound='bottom',command=self.switch)
            self.grid(column=col,row=ro)
            self.btn_id=button_id
            self.is_on=False
        def switch(self):
            if self.is_on:
                seq_list.remove(self.btn_id)
                self.config(bg='red',text=" ")
                self.check=False
            else:
                seq_list.append(self.btn_id)
                self.config(bg='green',text=f"{seq_list.index(self.btn_id)+1}")
                self.check=True
            self.is_on = not self.is_on
        
#this function creates the userhash based on the sequence of images and updates them to the database
    def get_usr_hash():
        global hash_value
        global sign_up_seq_run_check
        hash_value=0
        key=''
        for j in seq_list:
           key+=str(j)
        for i in range(n_img):
            hash1=getlsbhash(img_btn_dict[seq_list[i]],seq_list[i]+i+int(key))
            hash_value=hash1+hash_value
        cursor.execute("UPDATE USERDB set userhash=? WHERE Username=?",(hash_value.to_bytes(96,sys.byteorder),usr_name_input.usr_name))
        sign_up_seq_run_check=True
        root.destroy()
#this function checks if all the nine images are selected and calls the above function appropriately
    def get_usr_seq():
        val=0
        for i in range(n_img):
            if img_btn_list[i].check:
                val+=1
        if val == n_img:
            get_usr_hash()

#this function closes the previous root window
    def final_exit():
        root.destroy()
#the main sign_up program that makes use of the above classes and functions
    if ifdbexists("GraphAuthUserDatabase.db"):
        db_conn=sqlite3.connect("GraphAuthUserDatabase.db")
        cursor=db_conn.cursor()

        root=Tk()
        root.title("SIGNUP_Username")
        root.geometry("500x120")
        usr_name_input=GetUserName(root,0,0,cursor)
        root.mainloop()

        if usr_name_input.check:

            if usr_name_input.check:
                img_buttons=list()
                root=Tk()
                root.title("SIGNUP_Image")
                root.geometry("600x420")
                for i in range(n_img):
                    img_buttons.append(GetUserImage(root,0,i,i,cursor,usr_name_input.usr_name))
                submit_btn=Button(root,text="Submit",command=submit)
                submit_btn.grid(column=0,row=12)
                root.mainloop()
            if checked:
                img_btn_list=list()
                img_btn_dict=dict()
                for i in range(n_img):
                    query="SELECT img_"+str(i+1)+" FROM USERDB WHERE Username=?"
                    data=cursor.execute(query,(usr_name_input.usr_name,))
                    f="file"+str(i)
                    file_name=os.path.join(final_directory,f)
                    with open(file_name,"wb") as file:
                        for byte in data:
                            file.write(byte[0])

                root=Tk()
                root.title("GraphAuth:Selection")
                root.geometry("700x600")
                for i in range(n_img):
                    f="file"+str(i)
                    file_name=os.path.join(final_directory,f)
                    img_btn_list.append(img_button(root,file_name,loc[i][0],loc[i][1],i))
                    img_btn_dict[i]=file_name

                submit_btn=Button(root,text="Submit",command=get_usr_seq)
                submit_btn.grid(column=0,row=3)
                root.mainloop()
                if sign_up_seq_run_check:
                    db_conn.commit()
                    for root, dirs, files in os.walk(final_directory):
                      for f in files:
                          os.unlink(os.path.join(root, f))
                      for d in dirs:
                          shutil.rmtree(os.path.join(root, d))
                    root=Tk()
                    root.title("Sign_UP Successful")
                    root.geometry("500x120")
                    lb1=Label(root,text="You have Signed_up successfully please close the application and start again to login!")
                    lb1.grid(column=0,row=0)
                    exit_btn=Button(root,text="Exit",command=final_exit)
                    exit_btn.grid(column=0,row=1)

                    root.mainloop()
                
        else:
             root=Tk()
             root.title("Signed_up!")
             root.geometry("300x120")
             lb1=Label(root,text="You are already signed up ! Please login to continue.")
             lb1.grid(column=0,row=0)
             exit_btn=Button(root,text="Exit",command=final_exit)
             exit_btn.grid(column=0,row=1)
             root.mainloop()
         
        db_conn.close()
    else:
        print("Database Does not Exist")
#this is the login app and it is also the first page that the user sees when the app is opened
#this function directs to the sign_up function if the sign_up button is pressed
def login_app():
    global seq_list
#function to get the username
    def name_input():
        global usr_name
        global usr_identified
        usr_name=usr_name_input.get()
        cursor.execute("SELECT Username FROM USERDB WHERE Username=?",(usr_name,))
        if not cursor.fetchall():
            lb2.config(text="Not present in database",fg="red")
        else:
            lb2.config(text="Present in database",fg="green")
            usr_identified=True
            
            root.destroy()
    def sign_up():
        root.destroy()
        db_conn.close()
        sign_up_app()

    def final_exit():
        root.destroy()
    class img_button(Button):
        btn_id=0
        check=False
        def __init__(self,root,image_name,col,ro,button_id):
            self.photo=Image.open(image_name)
            self.resized=self.photo.resize((150,150),Image.LANCZOS)
            self.img=ImageTk.PhotoImage(self.resized)
            Button.__init__(self,master=root,image=self.img,text=" ",bg='red',compound='bottom',command=self.switch)
            self.grid(column=col,row=ro)
            self.btn_id=button_id
            self.is_on=False
        def switch(self):
            if self.is_on:
                seq_list.remove(self.btn_id)
                self.config(bg='red',text=" ")
                self.check=False
            else:
                seq_list.append(self.btn_id)
                self.config(bg='green',text=f"{seq_list.index(self.btn_id)+1}")
                self.check=True
            self.is_on = not self.is_on
        

    def get_usr_hash():
        global hash_value
        hash_value=0
        key=''
        for j in seq_list:
           key+=str(j)
        for i in range(n_img):
            hash1=getlsbhash(img_btn_dict[seq_list[i]],seq_list[i]+i+int(key))
            hash_value=hash_value+hash1

        root.destroy()
    def get_usr_seq():
        val=0
        for i in range(n_img):
            if img_btn_list[i].check:
                val+=1
        if val == n_img:
            get_usr_hash()
        

    if ifdbexists("GraphAuthUserDatabase.db"):
        db_conn=sqlite3.connect("GraphAuthUserDatabase.db")
        cursor=db_conn.cursor()
        root=Tk()
        root.title("GraphAuth")
        root.geometry("500x120")

        lb1=Label(root,text="Enter your Username: ")
        lb1.grid(column=0,row=0)
        usr_name_input=Entry(root,width=25)
        usr_name_input.grid(column=1,row=0)
        usr_input_btn=Button(root,text="Submit",command=name_input)
        usr_input_btn.grid(column=2,row=0)
        lb2=Label(root,text="Empty")
        lb2.grid(column=3,row=0)

        lb3=Label(root,text="OR",fg='black')
        lb3.grid(column=1,row=1)

        sign_up=Button(root,text="Sign_up",command=sign_up)
        sign_up.grid(column=1,row=2)
        root.mainloop()
        if usr_identified:
                cursor.execute("SELECT tries FROM USERDB WHERE Username=?",(usr_name,))
                usr_tries=cursor.fetchall()[0][0]
                if usr_tries != 4:
                    img_btn_list=list()
                    img_btn_dict=dict()
                    for i in range(n_img):
                        query="SELECT img_"+str(i+1)+" FROM USERDB WHERE Username=?"
                        data=cursor.execute(query,(usr_name,))
                        f="file"+str(i)
                        file_name=os.path.join(final_directory,f)
                        with open(file_name,"wb") as file:
                            for byte in data:
                                file.write(byte[0])

                    root=Tk()
                    root.title("GraphAuth:Selection")
                    root.geometry("700x600")
                    random.shuffle(loc)
                    for i in range(n_img):
                        f="file"+str(i)
                        file_name=os.path.join(final_directory,f)
                        img_btn_list.append(img_button(root,file_name,loc[i][0],loc[i][1],i))
                        img_btn_dict[i]=file_name
                    submit_btn=Button(root,text="Submit",command=get_usr_seq)
                    submit_btn.grid(column=0,row=3)
                    root.mainloop()
                    for root, dirs, files in os.walk(final_directory):
                         for f in files:
                             os.unlink(os.path.join(root, f))
                         for d in dirs:
                             shutil.rmtree(os.path.join(root, d))
                    cursor.execute("SELECT userhash FROM USERDB WHERE Username=?",(usr_name,))
                    primary_hash=cursor.fetchall()[0][0]
                    if primary_hash== hash_value.to_bytes(96,sys.byteorder):
                        db_conn.close()
                        return True
                    else:
                        cursor.execute("UPDATE USERDB set tries=? WHERE Username=?",(usr_tries+1,usr_name))
                        db_conn.commit()
                        root=Tk()
                        root.title("ACCESS DENIED")
                        root.geometry("500x120")
                        text1="Tries Remaining: "+str(4-(usr_tries+1))
                        lb1=Label(root,text=text1)
                        lb1.grid(column=0,row=0)
                        exit_btn=Button(root,text="Exit",command=final_exit)
                        exit_btn.grid(column=0,row=1)
                        root.mainloop()
                        db_conn.close()
                        return False
                else:
                    db_conn.close()
                    return 404
        if db_conn:
            db_conn.close()
            
    else:
        print("Database does not exist")
    
def GraphAuth():
    output=login_app()
    if sign_up_run:
        return 5
    return output
