from coap import coap_client
import random

method_code = ""
uri = ""


if __name__ == '__main__':
    MesID = random.randint(1, 50000)
    payload = ""
    while True:
        method_code = input("Enter method:\n 1.Get\n2.POST\n3.PUT\n4.DELETE")
        uri = input("Enter uri-path: ")
        if method_code == '2' or method_code == '3':
            payload = input("Enter payload: ")
        content = input("enter contenttype: ")
        coap_client(method_code, uri, MesID, payload, int(content))
        MesID += 1


