import sys 

def say_hello(name):
    print(f"Hello, {name}!")

def main():
    name = sys.argv[1]
    say_hello(name)

if __name__ == "__main__":
    main()