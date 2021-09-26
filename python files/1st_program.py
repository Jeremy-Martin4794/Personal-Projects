again = 'y'

while again == 'y':
    user_input = input("enter a number: ")
    user_input = int(user_input)

    if (user_input%3 == 0) and (user_input%2 == 0):
        print("fizzbuzz")

    elif user_input%3 == 0:
        print("fizz")

    elif user_input%2 == 0:
        print("buzz")
    
    again = input("Do you want to select another number [y,n]? ")