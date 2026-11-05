import argparse

def say_hello(name, times):
    for i in range(times):
        print(f"Hello,{name}!")

def main():
    parser = argparse.ArgumentParser( 
        description="A program that greets someone."
    )
    parser.add_arguement("name", help="Name of the Person to greet")
    parser.add_arguement(
        "--times", type=int, default=1,
        help="Number of greetings(default: 1)"
    )
    args = parser.parse_args()
    say_hello(args.name, args.times)

    if __name__ == "__main__":
        main()