
def read_binary():
    try:
        with open(".env", "rb") as f:
            content = f.read()
            print(f"RAW BYTES: {content}")
            try:
                print(f"DECODED: {content.decode('utf-8')}")
            except:
                print("Decode failed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_binary()
