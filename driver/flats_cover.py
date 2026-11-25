#!/usr/bin/env python
import time
import threading
import serial
from pyndigo.driver import *
from pyndigo.utils import print_msg as pp


class FlatsCoverDevice(StandardDriverDevice):
    def __init__(self, driver):
        super().__init__(driver, "Flats Cover")

        prop = self.add_text_property(
            "DEVICE_PORT",
            STATE_OK,
            PERM_RW,
            label="Device Port",
            group="Main",
        )
        prop.add_text("PORT", "/dev/ttyUSB0", label="Port")
        self.add_property_listener(prop, self.serial_port) 

        prop = self.add_text_property(
            "FIRMWARE_VERSION",
            STATE_OK,
            PERM_RO,
            label="Firmware",
            group="Main",
        )
        prop.add_text("FIRMWARE_VERSION", "--", label="Firmware Version")      

    def get_device_name(self) -> str: 
        return "Flats Panel"

    def get_device_driver(self) -> str:       
        return "Pyndigo Flats Panel"

    def get_device_version(self) -> str:
        return "1.0"

    def get_device_interface(self) -> str:
        return "Aux"

    def readFromSerial(self, port, baudrate):
        self.serialPort = serial.Serial(port, baudrate=baudrate, timeout=3)

        # Open SerialPort
        if not self.serialPort.isOpen():
            self.serialPort.open()

        while not self.stop_thread:
            line = self.serialPort.readline()
            line2 = line.decode("latin-1").strip()
            # pp(line2)

            if (line2.startswith("VERSION ")):
                v = line2[8:]
                prop = self.get_property("FIRMWARE_VERSION")
                prop.get_item("FIRMWARE_VERSION").set_value(v)
                self.send_property_update(prop)

            if (line2.startswith("STATUS ")):
                elems = line2.split(" ")

                if elems[1] == "0":
                    prop = self.set_switch_on("AUX_COVER", item_names=["CLOSE"], state = STATE_OK)
                else:
                    prop = self.set_switch_on("AUX_COVER", item_names=["OPEN"], state = STATE_OK)
                self.send_property_update(prop)

                if elems[2] == "0":
                    prop = self.set_switch_on("AUX_LIGHT_SWITCH", item_names=["OFF"], state = STATE_OK)
                else:
                    prop = self.set_switch_on("AUX_LIGHT_SWITCH", item_names=["ON"], state = STATE_OK)
                self.send_property_update(prop)

                prop = self.set_value("AUX_WEATHER", "TEMPERATURE", elems[3], state = STATE_OK)
                self.send_property_update(prop)                  

                if elems[4] == "0":
                    prop = self.set_switch_on("CONTINUOUS_STATUS_MESSAGE", item_names=["CONTINUOUS_OFF"], state = STATE_OK)
                else:
                    prop = self.set_switch_on("CONTINUOUS_STATUS_MESSAGE", item_names=["CONTINUOUS_ON"], state = STATE_OK)
                self.send_property_update(prop)

                prop = self.set_value("MESSAGE_INTERVAL", "MESSAGE_INTERVAL", elems[5], state = STATE_OK)
                self.send_property_update(prop)  

        self.serialPort.close()

        prop = self.get_property("FIRMWARE_VERSION")
        prop.get_item("FIRMWARE_VERSION").set_value("--")
        self.send_property_update(prop)
        
        return

    def client_ask_connect(self):
        thread = None

        self.stop_thread = False

        thread = threading.Thread(
            target=self.readFromSerial,
            args=(
                self.get_property("DEVICE_PORT").get_item("PORT").get_value(),
                9600,
            ),
        )

        thread.start()

        time.sleep(3)
        self.send_message_serial_port("VERSION")

        prop = self.add_switch_property(
            "AUX_COVER",
            STATE_OK,
            PERM_RW,
            RULE_ONE_OF_MANY,
            label="Cover",
            group="Control",
        )
        prop.add_switch("OPEN", SWITCH_OFF, label="Opened")
        prop.add_switch("CLOSE", SWITCH_ON, label="Closed")                
        self.get_driver().send_property_definition(prop)
        self.add_property_listener(prop, self.open_close_lid)         
     

        prop2 = self.add_switch_property(
            "AUX_LIGHT_SWITCH",
            STATE_OK,
            PERM_RW,
            RULE_ONE_OF_MANY,
            label="Light Status",
            group="Control",
        )
        prop2.add_switch("ON", SWITCH_OFF, label="Light On")
        prop2.add_switch("OFF", SWITCH_ON, label="Light Off") 
        self.add_property_listener(prop2, self.light_switch)               
        self.get_driver().send_property_definition(prop2)  

        prop3 = self.add_text_property(
            "AUX_WEATHER",
            STATE_OK,
            PERM_RO,
            label="Temperature",
            group="Control",
        )
        prop3.add_text("TEMPERATURE", "--", label="Temperature") 
        self.get_driver().send_property_definition(prop3)   

        prop4 = self.add_switch_property(
            "CONTINUOUS_STATUS_MESSAGE",
            STATE_OK,
            PERM_RW,
            RULE_ONE_OF_MANY,
            label="Continuous Status Message",
            group="Control",
        )
        prop4.add_switch("CONTINUOUS_ON", SWITCH_OFF, label="Messages On")
        prop4.add_switch("CONTINUOUS_OFF", SWITCH_ON, label="Messages Off")       
        self.add_property_listener(prop4, self.messages_switch)  
        self.get_driver().send_property_definition(prop4)   

        prop5 = self.add_number_property(
            "MESSAGE_INTERVAL",
            STATE_OK,
            PERM_RW,
            label="Message Interval",
            group="Control",
        )
        prop5.add_number("MESSAGE_INTERVAL", "30", "%.0f", 0, 120, 1, label="Interval") 
        self.add_property_listener(prop5, self.message_interval_changed)        
        self.get_driver().send_property_definition(prop5)    

        prop = self.set_switch_on("CONNECTION", item_names=["CONNECTED"], state = STATE_OK)
        self.send_property_update(prop)           
   

    def client_ask_disconnect(self):
        self.stop_thread = True        

        self.remove_property(self.get_property("AUX_COVER"))        
        self.remove_property(self.get_property("AUX_LIGHT_SWITCH")) 
        self.remove_property(self.get_property("AUX_WEATHER"))    
        self.remove_property(self.get_property("CONTINUOUS_STATUS_MESSAGE")) 
        self.remove_property(self.get_property("MESSAGE_INTERVAL")) 

        prop = self.set_switch_on("CONNECTION", item_names=["DISCONNECTED"], state = STATE_OK)
        self.send_property_update(prop)


    def message_interval_changed(self, prop: PyndigoProperty, items: dict):
        it = items.get("MESSAGE_INTERVAL")

        prop.set_busy()
        self.send_property_update(prop)

        if (it != None):
            self.send_message_serial_port("INTERVAL "+ it['value'])


    def open_close_lid(self, prop: PyndigoProperty, items: dict):
        it = items.get("OPEN")
 
        prop.set_busy()
        self.send_property_update(prop)

        if it.get("value") == SWITCH_ON:
            self.send_message_serial_port("OPEN")
        else:
            self.send_message_serial_port("CLOSE")

    def light_switch(self, prop: PyndigoProperty, items: dict):
        it = items.get("ON")

        prop.set_busy()
        self.send_property_update(prop)

        if it.get("value") == SWITCH_ON:
            self.send_message_serial_port("LON")
        else:
            self.send_message_serial_port("LOFF")         

    def messages_switch(self, prop: PyndigoProperty, items: dict):
        it = items.get("CONTINUOUS_ON")

        prop.set_busy()
        self.send_property_update(prop)

        if it.get("value") == SWITCH_ON:
            self.send_message_serial_port("START")
        else:
            self.send_message_serial_port("STOP")   

    def serial_port(self, prop: PyndigoProperty, items: dict):
        # pp(items)
        it = items["PORT"]['value']
        # pp(it)
        prop.get_item("PORT").set_value(it)
        prop.set_ok()
        self.send_property_update(prop)
           

    def send_message_serial_port(self, message: str):
        self.serialPort.write(str.encode(message + "\n"));
        self.serialPort.flush();

dr = PyndigoDriver("Flats Cover Driver")

dev = FlatsCoverDevice(dr)

dr.read()


