
def read_sol():
    try:
        with open("solution.txt", "r") as f:
            for line in f:
                print(line.strip())
    except Exception as e:
        print(e)

if __name__ == "__main__":
    read_sol()
