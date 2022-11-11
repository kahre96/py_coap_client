import socket
from bitstring import ConstBitStream, BitArray, ReadError
import codecs

def coap_client(methodcode, uri, messageID, payload="", contenttype=""):

    uri_path = ""
    body = ""
    contentopt= ""


    # adds uri path to options if there is one
    if uri != "":
        urilen = len(uri)
        optionhex = uri.encode('utf-8').hex()
        uri_path = f"b{urilen}{optionhex}"
    if contenttype != "":
        content = ""
        if contenttype == 0:
            contentlength = 0
        else:
            contentlength = 1
            content = hex(contenttype)

        contentopt= f"1{contentlength}{content[2:]}"

    MesID= hex(messageID)

    if methodcode == '2' or methodcode == '3':
        pay_load = payload.encode('utf-8').hex()
        body = f"FF {pay_load}"

    msgFromClient = f"50 0{methodcode} {MesID[2:]} {uri_path} {contentopt} {body}"

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
    print("Response Code: ", s.read('int:3'), ".", s.read('int:5'))
    print("Message ID: ", s.read('uint:16'))

    optionnr = 1
    optioncounter = 0
    while True:
        try:
            optiondelta = s.read('uint:4')
            optionlength = s.read('uint:4')

            # read extended optiondelta
            if optiondelta == 14:
                optiondelta = s.read('uint:16') +269

            if optiondelta == 13:
                optiondelta = s.read('uint:8') +13
            optioncounter += optiondelta

            # read extended optionlength
            if optionlength == 14:
                optionlength = s.read('uint:16') + 269
            if optionlength == 13:
                optionlength = s.read('uint:8') + 13
            
            readlength = optionlength*8
            optvalue = s.read(f'hex:{readlength}')

            opaqueopt = (1, 4)
            stringopts = (3, 8, 11, 15, 20, 35, 39)
            uintopts = (7, 12, 14, 17, 28, 60)
            blockopts = (23, 27)
            if optvalue == '':
                valuestring = ""
            elif optioncounter in opaqueopt:
                valuestring = f"opaque: {optvalue}"
            elif optioncounter in stringopts:
                valuestring = f"string: {bytes.fromhex(optvalue).decode('utf-8')}"
            elif optioncounter in uintopts:
                valuestring = f"uint: {int(optvalue, 16)}"
            elif optioncounter in blockopts:
                valuestring = "its a block"
            else:
                valuestring = "could not read value"
            #valuestring = codecs.decode(optvalue, "hex").decode('utf-8')
            #valuestring = optvalue.decode("utf-8")
            print("optionnr: ", optionnr)
            print("optioncode: ", optioncounter)
            print("optionlength: ", optionlength)
            print("optionvalue: ", valuestring)

            optionnr += 1

        except ReadError:
            # print(ReadError)
            # print("cant read optionvalue, ignore if option was empty")
            break

    message_content = body.decode("utf-8")

    print("Payload:", message_content)

