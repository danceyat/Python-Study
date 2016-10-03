"""
sorted(iterable[, key][, reverse])

Return a new sorted list from the items in iterable.

Has two optional arguments which must be specified as keyword arguments.

key specifies a function of one argument that is used to extract a comparison key from each list element: key=str.lower. The default value is None (compare the elements directly).

reverse is a boolean value. If set to True, then the list elements are sorted as if each comparison were reversed.

Use functools.cmp_to_key() to convert an old-style cmp function to a key function.

The built-in sorted() function is guaranteed to be stable. A sort is stable if it guarantees not to change the relative order of elements that compare equal — this is helpful for sorting in multiple passes (for example, sort by department, then by salary grade).
"""

# compare to list.sort() method which modifies the list in-place and returns
# None, sorted() will build a new sorted list instead
print(sorted([5, 2, 3, 1, 4]))

# key function use str.lower as default
print(sorted("This is a test string from Andrew".split(), key=str.lower))
# sort by age
student_tuples = [
    ('john', 'A', 15),
    ('jane', 'B', 12),
    ('dave', 'B', 10),
]
print(sorted(student_tuples, key=lambda student: student[2]))

from operator import itemgetter
# or use itemgetter() from operator module
print(sorted(student_tuples, key=itemgetter(2)))
# sort by grade then by age
print(sorted(student_tuples, key=itemgetter(1, 2)))
