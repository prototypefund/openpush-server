from tests.utils import CurlClient


c = CurlClient("http://127.0.0.1:5000/subscribe", "6SUxZ5Vj9aYffe2YxqYc0KQbxac")

c.get()

input("Press Enter to continue...")
while True:
    c.get()

print(c.buffer.read().decode())
c.buffer.getvalue().decode().split("\n\n")
