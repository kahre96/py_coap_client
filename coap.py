import socket
from bitstring import ConstBitStream,BitArray


def coap_client(methodcode, uri, messageID, payload=""):

    uri_path = ""
    body = ""

    # adds uri path to options if there is one
    if uri != "":
        urilen = len(uri)
        optionhex = uri.encode('utf-8').hex()
        uri_path = f"B{urilen} {optionhex}"

    MesID= hex(messageID)

    if methodcode != 1:
        pay_load = payload.encode('utf-8').hex()
        body = f"FF {pay_load}"

    msgFromClient = f'50 0{methodcode} {MesID[2:]} {uri_path}{body}'

    bytesToSend = bytes.fromhex(msgFromClient)

    serverAddressPort = ("coap.me", 5683)

    packet = bytearray(4096)

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom_into(packet)

    byte = bytes([0xff])
    byte2 = bytes(3)

    header, body = packet.split(byte, 1)
    body, useless = body.split(byte2, 1)

    bits = BitArray(header)

    s = ConstBitStream(bits)

    print("version: ", s.read('int:2'))
    print("T: ", s.read('int:2'))
    print("TKL: ", s.read('bin:4'))
    print("Response Code: ", s.read('bin:8'))
    print("Message ID: ", s.read('uint:16'))


    message_content = body.decode("utf-8")

    print("Payload:",message_content)

