result={}
row_count=0
with open("atm.csv", newline="") as file:
    reader = csv.reader(file)
with open("atm.csv", "r") as file:
    for line in file:
        line = line.strip()
        row = line.split(",")

        if row_count == 0:
            headers = row
            for h in headers:
                result[h] = []
        else:
            result[headers[0]] = result[headers[0]] + [row[0]]
            result[headers[1]] = result[headers[1]] + [row[1]]
            result[headers[2]] = result[headers[2]] + [row[2]]

        row_count += 1


print(result)
while True:
    print("welcome to atm")
    print("1. login 2. register 3. exit")
    try:
        option=int(input("enter the option:"))
        if option==1:   

            name=input("enter the name :")
            try:
                if name in result["name"]:
                    index=result["name"].index(name)
                    print(f"welcome {name}")
                    password=input("enter the password : ")
                    try:
                        if password==result["password"][index]:
                            print("password is correct")
                            print("login successful")
                        else:
                            print("check the password")
                    except ValueError:
                        print("check the password")
                    except TypeError:
                        print("check the password")
                else:
                    print(f"{name} user not found")        
            except ValueError:
                    print(f"check the input")
        elif option==2:
            name=input("enter the name :")
            if name in result["name"]:
                print(f"{name} user already exists")
            else:
                password=input("enter the password : ")
                with open("atm.csv", "a") as file:
                    file.write(f"\n{name},{password},1")

                print(f"{name} user registered successfully")
        else:
            print("thank you for using atm")
            break                    
    except ValueError:
        print("input should be a number")