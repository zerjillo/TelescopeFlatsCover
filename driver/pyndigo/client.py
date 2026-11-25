'''
asdfasdf asdfasdfasf asdfasdfasdfasdf asd fa fafasfasdfasdf asdfaf faf asfafafaf  asdfd fas sdfasdfsfa fa
'''
import asyncio
import json
import threading

from .common import *


class PyndigoClient(asyncio.Protocol):
    def __init__(self, name, host, port):
        self._name = name
        self._host = host
        self._port = port
        self._client_devices = {}
        self._timestamp = 0
        self._message = 0
        self._transport = None

    def get_client_devices(self) -> dict:
        return self._client_devices.copy()
    
    def get_name(self) -> str:
        return self._name
    
    def get_client_device(self, device_name) -> PyndigoDevice:
        return self._client_devices.get(device_name)
    
    def _add_client_device(self, device: PyndigoDevice):
        self._client_devices[device.get_name()] = device

    def _remove_client_device(self, deviceName: str, timestamp, message: str):
        if deviceName in self._client_devices:        
            self._client_devices.pop(deviceName)
            self._timestamp = timestamp
            self._message = message

            print("Removing device " + deviceName)               

    def _update_message(self, timestamp, message):
        self._timestamp = timestamp
        self._message = message

    def get_timestamp(self):
        return self._timestamp
    
    def get_message(self):
        return self._message

    
    def stablish_connection(self):
        x = threading.Thread(target=self._thread_stablish_connection)
        x.start()


    def _thread_stablish_connection(self):
        #loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        coro = loop.create_connection(lambda: self, self._host, self._port)
        print("1")
        loop.run_until_complete(coro)
        print("2")
        loop.run_forever()
        print("3")
        loop.close()
        print("4")
        
    def connection_made(self, transport):
        self._transport = transport

        message = { "getProperties": {"version": 512, "client": self._name} }

        self._writeMsg(message)

        #self._transport.write(message.encode())
        print('data sent: {}'.format(message))

    def data_received(self, data):
        dataR = "[" + data.decode().replace("}{", "},{") + "]"
        #print('data received: {}'.format(dataR))

        y = json.loads(dataR)
        #print(yaml.dump(y, default_flow_style=False))

        self._parse_messages(y)

    def _parse_messages(self, messages):
        print(messages)
        for m in messages:
            for key, value in m.items():
                if key.startswith("def"):
                    dev = self._get_device_or_create(value['device'])

                    prop = dev.get_property(value["name"])

                    if prop == None:  # If the property does not exist. Avoid changing existing properties
                        if key == "defTextVector":
                            type = TYPE_TEXT
                        elif key == "defNumberVector":
                            type = TYPE_NUMBER
                        elif key == "defSwitchVector":
                            type = TYPE_SWITCH
                        elif key == "defLightVector":
                            type = TYPE_LIGHT
                        else:
                            type = TYPE_BLOB

                        prop = PyndigoProperty(dev, type, _decoded_json = value) # Also gets added to the device
                        
                        self.property_has_changed(prop)

                elif key.startswith("set"):
                    dev = self.get_client_device(value['device'])

                    if dev != None:
                        prop = dev.get_property(value['name'])

                        prop._update(_decoded_json = value)

                        self.property_has_changed(prop)

                elif key == "message":
                    devName = value.get('device')
                    message = value.get('message')
                    timestamp = value.get('timestamp')

                    if devName != None:
                        dev = self.get_client_device(devName)

                        if dev != None:
                            dev._update_message(timestamp, message)

                            self.device_message_arrived(dev)

                    else:
                        self._update_message(timestamp, message)

                        self.client_message_arrived()

                elif key == "deleteProperty":
                    devName = value.get('device')
                    propertyName = value.get('name')
                    message = value.get('message')
                    timestamp = value.get('timestamp')

                    if devName != None:
                        dev = self.get_client_device(devName)

                        if dev != None:
                            if propertyName == None:  # Remove entire device
                                properties = dev.get_properties()

                                for p in properties.values():
                                    dev.remove_property(p.get_name(), message, timestamp)

                                self._remove_client_device(devName, message, timestamp)

                            else:
                                dev.remove_property(propertyName, message, timestamp)
    
                else:
                    print(key)

                
    # Gets a device in the client. If does not exists, creates one and returns it
    def _get_device_or_create(self, device_name):
        dev = self.get_client_device(device_name)

        if dev == None:
            dev = PyndigoDevice(device_name)
            self._add_client_device(dev)
    
        return dev
            

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()        


    def property_has_changed(self, prop: PyndigoProperty):
        pass

    def property_has_been_deleted(self, prop: PyndigoProperty ):
        pass

    def device_message_arrived(self, device: PyndigoDevice):
        pass

    def client_message_arrived(self):
        pass

    def propertyUpdate(self, prop: PyndigoProperty, itemValues: dict):
        if isinstance(prop, str):
            aux = prop.split("@", 1)
            devName = aux[0]         # Fallará, comprobarlo bien
            propName = aux[1]

            prop = self.get_client_device(devName).get_property(propName)


        if (not prop.is_read_only()):
            items = []

            for name, value in itemValues.items():
                items.append({"name": name, "value": value})

            propVect = {"device" : prop.get_device().get_name(), "name": prop.get_name(), "items": items}
            message = {"new" + prop.get_type() + "Vector": propVect}

            self._writeMsg(message)
    
    def _writeMsg(self, msg):
        if self._transport != None:
            msgStr = json.dumps(msg) + "\n"
            self._transport.write(msgStr.encode())
            print(" -> " + msgStr)


class MiCliente(PyndigoClient):
    def property_has_changed(self, prop: PyndigoProperty):
        print("%s has changed" % str(prop))

    def property_has_been_deleted(self, prop: PyndigoProperty ):
        print("%s has been deleted" % str(prop))

    def device_message_arrived(self, device: PyndigoDevice):
        print("%s has received a message" % str(device))

    def client_message_arrived(self):
        print("Client has received a message")

'''
client = MiCliente("Mi cliente", "127.0.0.1", 7624)

client.stablish_connection()

time.sleep(5)

client.propertyUpdate("CCD Imager Simulator@CONNECTION", {"CONNECTED": True, "DISCONNECTED": False})

time.sleep(10)

print("Han pasado diez segundos")

devs = client.get_devices()

print(devs)
for dn, d in devs.items():
    print(d.get_name())

    props = d.get_properties()

    for pn, p in props.items():
        print("    " + str(p))

        items = p.get_items()

        for inn, i in items.items():
            print("        " + str(i))
'''
