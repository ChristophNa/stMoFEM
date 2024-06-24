from time import sleep
with open("hello.txt", "w") as f:
    f.write("Hello from hello.py")
for i in range(200):
    with open("hello.txt", "a") as f:
        f.write(f"\nHello No.{i} from hello.py")
    sleep(10)