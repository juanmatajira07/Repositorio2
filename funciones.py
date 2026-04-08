def primo(n):
    for i in range(2,n):
        if n%i ==0:
            return False
    return False

def palindromo(s):
    return s==s[::-1]