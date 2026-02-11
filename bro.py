class Bro:
    def __init__(self,name,size,for_sale):
        self.name=name
        self.size=size
        self.for_sale=for_sale

    def start_Bro(self):
        print(f"{self.name} is on")    

    def stop_bro(self):
        print("jayboy is off")

bro1=Bro("jayboy","moderate","no")
bro2=Bro("manu","moderate","yes")
bro3=Bro("manu33","moderate","yes")
bro4=Bro("manu2","moderate","yes")
bro5=Bro("manu1","moderate","yes")

print(bro1.name)
print(bro2.name)
print(f"{bro1.name} has {bro1.size} size")
bro1.start_Bro()
bro2.start_Bro()




