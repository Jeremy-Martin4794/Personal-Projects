
lst = [4,2,8,1,5,6,3,7,10,9]
lst.sort()

user_input = int(input("enter a number to search for: "))
found = False

first = lst[0]
last = len(lst) - 1
mid = int((first+last)/2)
searches = 1

while (first <= last) and (found == False):
    mid = (first+last)//2

    if lst[mid] == user_input:
        print(user_input, "is in the list! ")
        found = True

    else:
        if lst[mid] < user_input:
            first = mid + 1
            searches = searches + 1

        else:
            last = mid - 1
            searches = searches + 1

print(searches, "searches ")
