# class addition():
#     def __init__(self, a, b):
#         c = a+b
#         print(c)
#     def subtraction(self, a, b):
#         c = a-b
#         print(c)

# a = 10
# b = 5
# obj = addition(a, b)
# obj.subtraction(a, b)
    

# student_marks = [[
#     ['Name', ['A', 'B', 'C', 'D', 'E']],
#     ['Ankit', [41, 34, 45, 55, 63]],
#     ['Ravi', [23, 45, 67, 89, 12]],
#     ['Raja', [12, 34, 56, 78, 90]],
#     ['Pranav', [23, 45, 67, 89, 12]],
#     ['Amit', [12, 34, 56, 78, 90]],
#     ['Ajay', [23, 45, 67, 89, 12]]
# ]]

# data = student_marks[0]
# subject_name = data[0][1]

# final_list = []

# for entry in data[1:]:
#     name = entry[0]
#     marks = entry[1]
#     student_dict = {"name": name}
#     for i, subject in enumerate(subject_name):
#         student_dict[subject] = marks[i]
#         final_list.append(student_dict)
# print(final_list)

        
# data = student_marks[0]  # Remove one level of nesting

# subject_names = data[0][1]  # ['A', 'B', 'C', 'D', 'E']

# students = []

# for entry in data[1:]:
#     name = entry[0]
#     marks = entry[1]
#     student_dict = {"Name": name}
#     for i, subject in enumerate(subject_names):
#         student_dict[subject] = marks[i]
#     students.append(student_dict)

# # Example output
# for student in students:
#     print(student)


# 1.
    # *
    # **
    # ***
    # ****
    # *****

# for i in range(0,4):
#     for j in range(0, 4):
#         if j<=i:
#             print("*", end='')
#         else:
#             print("", end='')
#     print()


# 2.
    #     *
    #    **
    #   ***
    #  ****
    # *****

# for i in range(1, 5):
#     for j in range(1, 5):
#         if j>=5-i:
#             print(j, end='')
#         else:
#             print(" ", end="")
#     print()

# 3.
    # *****
    # ****
    # ***
    # **
    # *

# def pattern():
#     for i in range(1, 5):
#         for j in range(1, 5):
#             if j<=5-i:
#                 print(j, end="")
#         print(" ")
# pattern()


# 4.
        # j= 1,2,3,4 
# i=  1   # ****
    # 2   #  ***
    # 3   #   **
    # 4   #    *


# def paturn():
#     for i in range(1, 5):
#         for j in range(1, 5):
#             if j>=i:
#                 print("*", end='')
#             else:
#                 print(' ', end='')
#         print()
# paturn() 

# 5.
        # j= 1,2,3,4,5,6,7 
# i=  1   #     *
    # 2   #    ***
    # 3   #   *****
    # 4   #  *******


# def paturn():
#     for i in range(1, 5):
#         for j in range(1, 8):
#             if j>=5-i and j<=3+i:
#                 print(j, end='')
#             else:
#                 print(' ', end='')
#         print()
# paturn()



# 8.
        # j= 1,2,3,4,5,6,7 

# i=  1    *******
    # 2    *** ***
    # 3    **   **
    # 4    *     *

# for i in range(1, 5):
#     for j in range(1, 8):
#         if j<=5-i or j>=3+i:
#             print(j, end='')
#         else:
#             print(' ', end='')
#     print()


# 11.
        # j= 1 2 3 4 5 6 7 8 9 10 11

# i=  1               *
    # 2             * * *
    # 3           * * * * *
    # 4         * * * * * * *
    # 5       * * * * * * * * *
    # 6     * * * * * * * * * * *
    # 7       * * * * * * * * *
    # 8         * * * * * * *
    # 9           * * * * *
    # 10            * * * 
    # 11              *
    

# for i in range(1, 7):
#     for j in range(1, 12):
#         if j>=7-i and j<=5+i:
#             print("*", end=' ')
#         else:
#             print(' ', end=' ')
#     print()
# for i in range(1, 7):
#     for j in range(1, 12):
#         if j>i and j<=11-i:
#             print("*", end=' ')
#         else:
#             print(' ', end=' ')
#     print()


# 12.
        # j= 1 2 3 4 5 6 7 

# i=  1     * # # # # # *
    # 2     # * # # # * #
    # 3     # # * # * # #
    # 4     # # # * # # #
    # 5     # # * # * # #
    # 6     # * # # # * #
    # 7     * # # # # # * 
    
# for i in range(1, 8):
#     for j in range(1, 8):
#         if j==i or j==8-i:
#             print("*", end=' ')
#         else:
#             print('#', end=' ')
#     print()
 

# 13
  
# i=  1    1   
    # 2    1  2   
    # 3    2  3  5 
    # 4    5  7  10 15
    # 5    15 20 27 37 52


# l1 = [1]
# l2 = []

# for row in range(1, 1+int(input("enter numbert"))):
#     l2.append(l1[-1])
#     for e in l1:
#         l2.append(e+l2[-1])
#     print(l1)
#     l1=list(l2)
#     l2.clear()