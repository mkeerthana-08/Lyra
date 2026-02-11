def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                duplicates.append(arr[i])
    return duplicates


def simple_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total
