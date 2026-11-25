"""
This module contain the basic classes upon which INDIGO drivers 
(and agents) are built. A driver should extend 
:obj:`~pyndigo.driver.StandardDriverDevice` or even
:obj:`~pyndigo.driver.PyndigoDriverDevice`.

Classes
-------
:obj:`~pyndigo.driver.PyndigoDriverDevice`
    Base class for a driver device. This class allows the allocation of
    properties and their handlers.
:obj:`~pyndigo.driver.StandardDriverDevice`
    A :obj:`~pyndigo.driver.PyndigoDriverDevice` that includes the 
    standard ``CONNECTION`` property and its handler.
:obj:`~pyndigo.driver.PyndigoDriver`
    The main class that allows the creation of Drivers for one or more
    Devices.
"""

from xml.etree.ElementTree import XMLPullParser
from typing import Callable
import sys
from .common import *
from pyndigo.utils import print_msg as pp

class PyndigoDriverDevice:
    """
    This class can be extended in order to develop a Device that can
    be used in a Driver. It provides the basic functionality to add
    properties and handlers for them. Take into account that for most of
    the Devices it is usually better to extend
    :obj:`~pyndigo.driver.StandardDriverDevice` which already implements
    the standard ``CONNECTION`` property.

    To add properties you should use the methods:

        * :obj:`PyndigoDriverDevice.add_text_property(...)
          <pyndigo.driver.PyndigoDriverDevice.add_text_property>`
        * :obj:`PyndigoDriverDevice.add_number_property(...)
          <pyndigo.driver.PyndigoDriverDevice.add_number_property>`
        * :obj:`PyndigoDriverDevice.add_switch_property(...)
          <pyndigo.driver.PyndigoDriverDevice.add_switch_property>`
        * :obj:`PyndigoDriverDevice.add_light_property(...)
          <pyndigo.driver.PyndigoDriverDevice.add_light_property>`
        * :obj:`PyndigoDriverDevice.add_blob_property(...)
          <pyndigo.driver.PyndigoDriverDevice.add_blob_property>`

    In addition you can add/remove handlers that listen to property
    changes from the Clients using the methods:

        * :obj:`PyndigoDriverDevice.add_property_listener(...)
          <pyndigo.driver.PyndigoDriverDevice.add_property_listener>`
        * :obj:`PyndigoDriverDevice.remove_property_listener(...)
          <pyndigo.driver.PyndigoDriverDevice.remove_property_listener>`
    """

    def __init__(self, driver: "PyndigoDriver", name: str):
        """
        Constructs a new PyndigoDriverDevice. This constructor should not
        be directly used as Devices are supposed to extend this class.

        Parameters
        ----------
        driver : PyndigoDriver
            The Driver in which the Device is integrated
        name : str
            A name for the device.
        """
        self._name = name
        self._properties = {}
        self._listener_properties = {}
        self._driver = driver
        driver._add_driver_device(self)

    def get_driver(self) -> "PyndigoDriver":
        """
            Gets the Driver for the device.

        Returns
        -------
        PyndigoDriver
            The Driver for the Device.
        """
        return self._driver

    def add_property_listener(
        self,
        prop: PyndigoProperty | str,
        func: Callable[[PyndigoProperty, list[dict]], None],
    ) -> None:
        """
        Adds a method of the class to be a listener when a Client asks
        for changes in a particular property.

        Parameters
        ----------
        property : PyndigoProperty | str
            The Property (or its name) to listen for Client changes on it.
        func : Callable[[PyndigoProperty, list[dict]], None]
            The method to be called when a Client ask for changes in the
            property.
        """
        name = prop

        if isinstance(name, PyndigoProperty):
            name = prop.get_name()
        self._listener_properties[name] = func

    def remove_property_listener(self, prop: PyndigoProperty | str) -> None:
        """
        Removes the listener associated to a Property.

        Parameters
        ----------
        prop : PyndigoProperty | str
            The Property (or its name) to remove its listener.
        """
        name = prop

        if isinstance(name, PyndigoProperty):
            name = prop.get_name()

        if self._listener_properties.get(name) is not None:
            self._listener_properties.pop(name)

    def add_text_property(
        self,
        name: str,
        state: str,
        perm: str,
        label: str = "",
        group: str = "",
        timeout=0,
        timestamp: str = None,
        message: str = None,
    ) -> PyndigoProperty:
        """
        Creates and adds a Text Property to the Device.

        Parameters
        ----------
        name : str
            Name of the Property.
        state : str
            Initial state of the Property. That is, one of
            :obj:`~pyndigo.common.STATE_OK`,
            :obj:`~pyndigo.common.STATE_BUSY`,
            :obj:`~pyndigo.common.STATE_ALERT` or
            :obj:`~pyndigo.common.STATE_IDLE`.
        perm : str
            The permissions for the Property. That is, one of
            :obj:`pyndigo.common.PERM_RW`, :obj:`pyndigo.common.PERM_RO`
            or :obj:`pyndigo.common.PERM_WO`.
        label : str, optional
            A label for the Property, typically used in GUIs, by default "".
        group : str, optional
            The group of the Property, tyically used to group properties
            in GUIs, by default "".
        timeout : int, optional
            Timeout for the Property, by default 0
        timestamp : str, optional
            Timestamp for the Property, by default None
        message : str, optional
            A message about the Property, by default None

        Returns
        -------
        PyndigoProperty
            The created and added Text Property.
        """
        prop = PyndigoProperty(
            self,
            TYPE_TEXT,
            name=name,
            state=state,
            perm=perm,
            label=label,
            group=group,
            timeout=timeout,
            timestamp=timestamp,
            message=message,
        )

        self._add_property(prop)

        return prop

    def add_number_property(
        self,
        name: str,
        state: str,
        perm: str,
        label: str = "",
        group: str = "",
        timeout=0,
        timestamp: str = None,
        message: str = None,
    ) -> PyndigoProperty:
        """
        Creates and adds a Number Property to the Device.

        Parameters
        ----------
        name : str
            Name of the Property.
        state : str
            Initial state of the Property. That is, one of
            :obj:`~pyndigo.common.STATE_OK`,
            :obj:`~pyndigo.common.STATE_BUSY`,
            :obj:`~pyndigo.common.STATE_ALERT` or
            :obj:`~pyndigo.common.STATE_IDLE`.
        perm : str
            The permissions for the Property. That is, one of
            :obj:`pyndigo.common.PERM_RW`, :obj:`pyndigo.common.PERM_RO`
            or :obj:`pyndigo.common.PERM_WO`.
        label : str, optional
            A label for the Property, typically used in GUIs, by default "".
        group : str, optional
            The group of the Property, tyically used to group properties
            in GUIs, by default "".
        timeout : int, optional
            Timeout for the Property, by default 0
        timestamp : str, optional
            Timestamp for the Property, by default None
        message : str, optional
            A message about the Property, by default None

        Returns
        -------
        PyndigoProperty
            The created and added Number Property.
        """
        prop = PyndigoProperty(
            self,
            TYPE_NUMBER,
            name=name,
            state=state,
            perm=perm,
            label=label,
            group=group,
            timeout=timeout,
            timestamp=timestamp,
            message=message,
        )

        self._add_property(prop)

        return prop

    def add_switch_property(
        self,
        name: str,
        state: str,
        perm: str,
        rule: str,
        label: str = "",
        group: str = "",
        timeout=0,
        timestamp: str = None,
        message: str = None,
    ) -> PyndigoProperty:
        """
        Creates and adds a Switch Property to the Device.

        Parameters
        ----------
        name : str
            Name of the Property.
        state : str
            Initial state of the Property. That is, one of
            :obj:`~pyndigo.common.STATE_OK`,
            :obj:`~pyndigo.common.STATE_BUSY`,
            :obj:`~pyndigo.common.STATE_ALERT` or
            :obj:`~pyndigo.common.STATE_IDLE`.
        perm : str
            The permissions for the Property. That is, one of
            :obj:`pyndigo.common.PERM_RW`, :obj:`pyndigo.common.PERM_RO`
            or :obj:`pyndigo.common.PERM_WO`.
        rule : str
            The rule of the switch property. That is, one of
            :obj:`pyndigo.common.RULE_ONEOFMANY`,
            :obj:`pyndigo.common.RULE_ATMOSTONE`,
            :obj:`pyndigo.common.RULE_ANYOFMANY`.
        label : str, optional
            A label for the Property, typically used in GUIs, by default "".
        group : str, optional
            The group of the Property, tyically used to group properties
            in GUIs, by default "".
        timeout : int, optional
            Timeout for the Property, by default 0
        timestamp : str, optional
            Timestamp for the Property, by default None
        message : str, optional
            A message about the Property, by default None

        Returns
        -------
        PyndigoProperty
            The created and added Switch Property.
        """
        prop = PyndigoProperty(
            self,
            TYPE_SWITCH,
            name=name,
            state=state,
            perm=perm,
            label=label,
            group=group,
            rule=rule,
            timeout=timeout,
            timestamp=timestamp,
            message=message,
        )

        self._add_property(prop)

        return prop

    def add_light_property(
        self,
        name: str,
        state: str,
        label: str = "",
        group: str = "",
        timestamp: str = None,
        message: str = None,
    ) -> PyndigoProperty:
        """
        Creates and adds a Light Property to the Device.

        Parameters
        ----------
        name : str
            Name of the Property.
        state : str
            Initial state of the Property. That is, one of
            :obj:`~pyndigo.common.STATE_OK`,
            :obj:`~pyndigo.common.STATE_BUSY`,
            :obj:`~pyndigo.common.STATE_ALERT` or
            :obj:`~pyndigo.common.STATE_IDLE`.
        label : str, optional
            A label for the Property, typically used in GUIs, by default "".
        group : str, optional
            The group of the Property, tyically used to group properties
            in GUIs, by default "".
        timestamp : str, optional
            Timestamp for the Property, by default None
        message : str, optional
            A message about the Property, by default None

        Returns
        -------
        PyndigoProperty
            The created and added Light Property.
        """
        prop = PyndigoProperty(
            self,
            TYPE_LIGHT,
            name=name,
            state=state,
            label=label,
            group=group,
            timestamp=timestamp,
            message=message,
        )

        self._add_property(prop)

        return prop

    def add_blob_property(
        self,
        name: str,
        state: str,
        perm: str,
        label: str = "",
        group: str = "",
        timeout=0,
        timestamp: str = None,
        message: str = None,
    ) -> PyndigoProperty:
        """
        Creates and adds a BLOB Property to the Device.

        Parameters
        ----------
        name : str
            Name of the Property.
        state : str
            Initial state of the Property. That is, one of
            :obj:`~pyndigo.common.STATE_OK`,
            :obj:`~pyndigo.common.STATE_BUSY`,
            :obj:`~pyndigo.common.STATE_ALERT` or
            :obj:`~pyndigo.common.STATE_IDLE`.
        perm : str
            The permissions for the Property. That is, one of
            :obj:`pyndigo.common.PERM_RW`, :obj:`pyndigo.common.PERM_RO`
            or :obj:`pyndigo.common.PERM_WO`.
        label : str, optional
            A label for the Property, typically used in GUIs, by default "".
        group : str, optional
            The group of the Property, tyically used to group properties
            in GUIs, by default "".
        timeout : int, optional
            Timeout for the Property, by default 0
        timestamp : str, optional
            Timestamp for the Property, by default None
        message : str, optional
            A message about the Property, by default None

        Returns
        -------
        PyndigoProperty
            The created and added BLOB Property.
        """
        prop = PyndigoProperty(
            self,
            TYPE_BLOB,
            name=name,
            state=state,
            label=label,
            group=group,
            perm=perm,
            timeout=timeout,
            timestamp=timestamp,
            message=message,
        )

        self._add_property(prop)

        return prop

    def _add_property(self, prop: PyndigoProperty):
        self._properties[prop.get_name()] = prop

    def remove_property(
        self, prop: PyndigoProperty | str, timestamp: str = None, message: str = None
    ) -> None:
        """
        Removes a property from the Device. 

        Parameters
        ----------
        prop : PyndigoProperty | str
            The Property (or its name) to be removed from the Device.
        timestamp : str, optional
            A timestamp for the Clients, by default None
        message : str, optional
            A message for the Clients, by default None
        """
        name = prop

        if isinstance(prop, PyndigoProperty):
            name = prop.get_name()

        if name in self._properties:
            self.remove_property_listener(prop)
            
            self.get_driver().send_del_property(prop)       

            self._properties.pop(name)



     

    def get_properties(self) -> dict[str, PyndigoProperty]:
        """
        Gets all the properties of the Device.

        Returns
        -------
        dict[str, PyndigoProperty]
            A dictionary with all the properties of the Device. The key
            is the Property name.
        """
        return self._properties.copy()

    def get_property(self, prop: str) -> PyndigoProperty:
        """
        Gets the Property of the Device of a given name.

        Parameters
        ----------
        prop : str
            The name of the Property to get.

        Returns
        -------
        PyndigoProperty
            The Property of the Device. ``None`` if the Device has
            no property with the given name.
        """
        return self._properties.get(prop)

    def set_switch_on(self, prop: str, item_names = [], state = None):
        prop = self._get_property(prop)

        i = prop.get_items()

        for key, item in i.items():
            pp(key)
            pp(item_names)
            if key in item_names:
                pp("**")
                item.set_value(SWITCH_ON)
            else:
                item.set_value(SWITCH_OFF)

        if state != None:
            prop._set_state(state)

        return prop



    def set_value(self, prop: str, item_name: str, value: str | int, state = None) -> PyndigoProperty:
        """
        Sets a value for an Item of a Property of the Device. DOES NOT
        notify the clients of the change. If you want to notify the
        clients you should then call
        :obj:`~PyndigoDriverDevice.send_property_update`.

        Parameters
        ----------
        prop : str
            The name of the Property to update an Item.
        item_name : str
            The name of the item to set its value.
        value : str | int
            The new value of the item
        status : optionally, the status of the property

        Returns
        -------
        PyndigoProperty
            The updated Property. ``None`` if there was no Property
            with that name in the Device.
        """
        prop = self._get_property(prop)

        if prop is not None:
            item = prop.get_item(item_name)

            if item is not None:
                item.set_value(value)

            if (state != None):
                prop._set_state(state)

        return prop

    def set_values(
        self,
        prop: str,
        item_names_values: list[tuple[str, str | int]],
    ) -> PyndigoProperty:
        """
        Sets the values of several Items of a Property of the Device.
        DOES NOT notify the clients of the change. If you want to notify
        the clients you should then call
        :obj:`~PyndigoDriverDevice.send_property_update`.

        This is a shorthand for multiple consecutive
        :obj:`~PyndigoDriverDevice.send_value` calls.

        Parameters
        ----------
        prop : str
            The name of the Property to update some of its Items.
        item_names_values : list[tuple[str, str  |  int]]
            A list of pairs in the form ``(nameOfItem, valueOfItem)``.

        Returns
        -------
        PyndigoProperty
            The updated Property. ``None`` if there was no Property
            with that name in the Device.
        """
        prop = self._get_property(prop)

        if prop is not None:
            for item_name, value in item_names_values:
                item = prop.get_item(item_name)

                if item is not None:
                    item.set_value(value)

        return prop

    def get_value(self, prop: str, item_name: str) -> str | int:
        """
        Gets the value for an Item of a Property of the Device. Its a
        shorthand for code like:
        ``device.get_property(property_name).get_item(item_name).get_value()``

        Parameters
        ----------
        prop : str
            The name of the Property of the Device to get one of its
            items value.
        item_name : str
            The name of the Item to get its value.

        Returns
        -------
        str | int
            The value of the Item. ``None`` if there is no such Property
            or Item in the Device.
        """
        prop = self._get_property(prop)

        if prop is not None:
            item = prop.get_item(item_name)

            if item is not None:
                return item.get_value()

        return None

    def set_alert(self, prop: str) -> PyndigoProperty:
        """
        Sets the State of the Property as
        :obj:`~pyndigo.common.STATE_ALERT`. DOES NOT notify the clients
        of the change. If you want to notify the clients you should then
        call :obj:`~PyndigoDriverDevice.send_property_update`.

        Parameters
        ----------
        prop : str
            The name of the Property of the Device.

        Returns
        -------
        PyndigoProperty
            The Property with its state set as
            :obj:`~pyndigo.common.STATE_ALERT`.
        """
        prop = self._get_property(prop)

        prop.set_alert()

        return prop

    def set_ok(self, prop) -> PyndigoProperty:
        """
        Sets the State of the Property as
        :obj:`~pyndigo.common.STATE_OK`. DOES NOT notify the clients
        of the change. If you want to notify the clients you should then
        call :obj:`~PyndigoDriverDevice.send_property_update`.

        Parameters
        ----------
        prop : str
            The name of the Property of the Device.

        Returns
        -------
        PyndigoProperty
            The Property with its state set as
            :obj:`~pyndigo.common.STATE_OK`.
        """
        prop = self._get_property(prop)

        prop.set_ok()

        return prop

    def set_busy(self, prop) -> PyndigoProperty:
        """
        Sets the State of the Property as
        :obj:`~pyndigo.common.STATE_BUSY`. DOES NOT notify the clients
        of the change. If you want to notify the clients you should then
        call :obj:`~PyndigoDriverDevice.send_property_update`.

        Parameters
        ----------
        prop : str
            The name of the Property of the Device.

        Returns
        -------
        PyndigoProperty
            The Property with its state set as
            :obj:`~pyndigo.common.STATE_BUSY`.
        """
        prop = self._get_property(prop)

        prop.set_busy()

        return prop

    def set_idle(self, prop) -> PyndigoProperty:
        """
        Sets the State of the Property as
        :obj:`~pyndigo.common.STATE_IDLE`. DOES NOT notify the clients
        of the change. If you want to notify the clients you should then
        call :obj:`~PyndigoDriverDevice.send_property_update`.

        Parameters
        ----------
        prop : str
            The name of the Property of the Device.

        Returns
        -------
        PyndigoProperty
            The Property with its state set as
            :obj:`~pyndigo.common.STATE_IDLE`.
        """
        prop = self._get_property(prop)

        prop.set_idle()

        return prop

    def _get_property(self, prop):
        if isinstance(prop, str):
            prop = self.get_property(prop)

        return prop

    def get_name(self) -> str:
        """
        Gets the name of the Device.

        Returns
        -------
        str
            The name of the Device.
        """
        return self._name

    def _client_asks_for_change(
        self, prop: PyndigoProperty, items: dict[str, dict]
    ) -> None:
        if (
            self._listener_properties.get(prop.get_name()) is not None
        ):  # Check if in listeners
            func = self._listener_properties.get(prop.get_name())
            func(prop, items)

        self.client_asks_for_change(prop, items)

    def send_property_update(self, prop: str) -> None:
        """
        Sends the message to the clients that a Property has been updated.

        Parameters
        ----------
        prop : str
            The name of the Property that has been updated.
        """
        prop = self._get_property(prop)

        if prop is not None:
            self.get_driver().send_property_update(prop)

    def client_asks_for_change(self, prop: PyndigoProperty, items: dict[str, dict]):
        """
        This method is called when a client asks for a change in a
        particular Property. Typically overriden by subclasses to listen
        for Property changes if not using explicit listeners. See
        :obj:`PyndigoDriverDevice.add_property_listener` and
        :obj:`PyndigoDriverDevice.remove_property_listener`

        Parameters
        ----------
        prop : PyndigoProperty
            The Property to which a client has asked for changes.
        items : dict[dict]
            A dictionary of the updates for each Item that was asked for
            change by the client. The key is the name of the Item. The
            value is a dictionary with a ``"value"`` key that represents 
            the value that the client has asked for in the Item. If the
            property if a BLOB one, it may also contain a ``"size"``, 
            ``"format"`` and ``"url"`` keys.
        """


class StandardDriverDevice(PyndigoDriverDevice):
    """
    This class can be extended in order to develop a Device that can
    be used in a Driver. It adds the standard ``CONNECTION`` property
    that is handled by the :obj:`~client_ask_connect` and 
    :obj:`~client_ask_disconnect` methods.
    """
    def __init__(self, driver: "PyndigoDriver", name: str):
        """
        Constructs a new StandardDriverDevice. This constructor should not
        be directly used as Devices are supposed to extend this class.

        Parameters
        ----------
        driver : PyndigoDriver
            The Driver in which the Device is integrated
        name : str
            A name for the device.
        """
        super().__init__(driver, name)

        prop = self.add_switch_property(
            "CONNECTION",
            STATE_OK,
            PERM_RW,
            RULE_ONE_OF_MANY,
            label="Connection",
            group="Main",
        )

        prop.add_switch("CONNECTED", SWITCH_OFF, label="Connected")
        prop.add_switch("DISCONNECTED", SWITCH_ON, label="Disconnected")
        self.add_property_listener(prop, self._connection_changed)

        prop2 = self.add_text_property(
            "INFO",
            STATE_OK,
            PERM_RO,
            label = "Information",
            group = "Main",
        )

        prop2.add_text("DEVICE_NAME", self.get_device_name(), label="Device Name")
        prop2.add_text("DEVICE_DRIVER" , self.get_device_driver(), label="Device Driver")
        prop2.add_text("DEVICE_VERSION", self.get_device_version(), label="Driver Version")
        prop2.add_text("DEVICE_INTERFACE", self.get_device_interface(), label="Interface")

    def get_device_name(self) -> str: 
        """
        Returns de device name. This method should by implemented by subclasses.
        """        
        return ""

    def get_device_driver(self) -> str:
        """
        Returns the name of the driver. This method should by implemented by subclasses.
        """             
        return ""

    def get_device_version(self) -> str:
        """
        Returns the version of the driver. This method should by implemented by subclasses.
        """               
        return ""

    def get_device_interface(self) -> str:
        """
        Returns the interface type of the driver. This method should by implemented by subclasses.
        """       
        return ""

    def _connection_changed(self, prop: PyndigoProperty, items: dict):
        it = items.get("CONNECTED")
        if it == None:
            it = items.get("CONNECT")  # Old style connection

        if it.get("value") == SWITCH_ON:
            self.client_ask_connect()
        else:
            self.client_ask_disconnect()

    def client_ask_connect(self) -> None:
        """
        This method will be called when a client changes the 
        ``CONNECTION`` property to ``CONNECTED``. Usually the 
        ``CONNECTION`` property State should be changed to 
        :obj:`~Pyndigo.common.STATE_BUSY` (and
        updated to the client), the driver should do its connection logic
        and then change the state of the ``CONNECTION`` to 
        :obj:`~Pyndigo.common.STATE_OK`.

        Usually implemented by subclasses.
        """

    def client_ask_disconnect(self) -> None:
        """
        This method will be called when a client changes the 
        ``CONNECTION`` property to ``DISCONNECTED``. Usually the 
        ``CONNECTION`` property State should be changed to 
        :obj:`~Pyndigo.common.STATE_BUSY` (and
        updated to the client), the driver should do its disconnection 
        logic and then change the state of the ``CONNECTION`` to 
        :obj:`~Pyndigo.common.STATE_OK`.

        Usually implemented by subclasses.
        """


class PyndigoDriver:
    """
    This class is instantiated in order to create Drivers for one or
    more Devices.
    
    The main logic to control de Devices should be done extending the 
    classes :obj:`~Pyndigo.driver.StandardDriverDevice` or
    :obj:`~Pyndigo.driver.PyndigoDriverDevice`. 

    The usual sequence to use this class is:

        #. Create a :obj:`~Pyndigo.driver.PyndigoDriver`
        #. Create :obj:`~Pyndigo.driver.PyndigoDriverDevice` (one or more)
        #. Call the :obj:`~Pyndigo.driver.PyndigoDriver.read` method 
           which starts the routine of reading / writing from / to the clients.

    For example: ::

        dr = PyndigoDriver("My driver")
        MiOwnDevice(dr)
        MiOtherDevice(dr)
        dr.read()

    """
    def __init__(self, name: str):
        """
        Creates a Driver.

        Parameters
        ----------
        name : str
            The name of the Driver
        """
        self._name = name
        self._driver_devices = {}

    def get_driver_devices(self) -> dict[str, PyndigoDriverDevice]:
        """
        Gets all the Devices in the Driver

        Returns
        -------
        dict[str, PyndigoDriverDevice]
            A dictionary with all the Devices in the Driver. The key is 
            the name of the Device and the value is the device itself.
        """
        return self._driver_devices.copy()

    def get_name(self) -> str:
        """
        Gets the name of the driver

        Returns
        -------
        str
            The name of the Driver
        """
        return self._name

    def get_driver_device(self, device_name: str) -> PyndigoDriverDevice:
        """
        Gets a Device of the Driver by its name.

        Parameters
        ----------
        device_name : str
            The name of the desired Device.

        Returns
        -------
        PyndigoDriverDevice
            The desired Device. ``None`` if there is no Device with
            the provided name in the Driver.
        """
        return self._driver_devices.get(device_name)

    def _add_driver_device(self, device: PyndigoDriverDevice):
        self._driver_devices[device.get_name()] = device

    def read(self) -> None:
        """
        Main logic of the driver. It reads from standard input the 
        messages from the Clients (probably through a Server) and
        process the messages calling listeners in the Devices.

        It should be called once the initialization of the Driver is 
        done. It blocks the execution thread (which is the normal 
        behaviour for a Driver.
        """
        parser = XMLPullParser(events=["end"])
        parser.feed("<xml>")

        for line in sys.stdin:
            parser.feed(line)

            for event, elem in parser.read_events():
                print(elem.tag)

                if elem.tag == "getProperties":
                    if elem.get("switch") == "2.0":
                        self._send_message_to_client(
                            "<switchProtocol version='2.0'/>\n"
                        )

                    device_name = elem.get("device")
                    if device_name is not None:
                        d = self.get_driver_device(device_name)

                        if d is not None:
                            for pn, p in d.get_properties().items():
                                self.send_property_definition(p)
                    else:  # Send all devices
                        for dn, d in self.get_driver_devices().items():
                            for pn, p in d.get_properties().items():
                                self.send_property_definition(p)

                if elem.tag.startswith("new"):
                    device_name = elem.get("device")
                    if device_name is not None:
                        d = self.get_driver_device(device_name)

                        if d is not None:
                            prop_name = elem.get("name")

                            prop = d.get_property(prop_name)

                            if prop is not None:
                                timestamp = elem.get("timestamp")

                                items = {}
                                for subelem in elem.findall("one" + prop.get_type()):
                                    it = {"value": subelem.text}

                                    if prop.is_blob():
                                        it["size"] = subelem.get("size")
                                        it["format"] = subelem.get("format")

                                        if subelem.get("url") is not None:
                                            it["url"] = subelem.get("url")

                                    items[subelem.get("name")] = it

                                d._client_asks_for_change(prop, items)

    def send_property_definition(self, prop: PyndigoProperty) -> None:
        """
        Sends to the Clients the definition of a Property. Should be
        called by the Devices once a new Property is added (only once 
        and not necessary at the initilization of the Devices).

        Parameters
        ----------
        prop : PyndigoProperty
            The Property that has to be sent to the Clients.
        """
        xml = prop._get_def_xml()

        self._send_message_to_client(xml)

    def send_property_update(self, prop: PyndigoProperty, msg: str = None) -> None:
        """
        Sends to the Clients an updated Property. Should be called by the 
        Devices once a Property value or State has been changed.

        Parameters
        ----------
        prop : PyndigoProperty
            The Property whose updated has to be sent to the Clients.

        msg : str, optional
            A message to be sent along with the update, by default None
        """
        xml = prop._get_set_xml(msg)

        self._send_message_to_client(xml)

    def send_del_property(self, prop: PyndigoProperty, msg: str = None) -> None:
        """
        Sends to the Clients a property that has to be removed. 

        Parameters
        ----------
        prop : PyndigoProperty
            The Property that have to be removed from the Clients.

        msg : str, optional
            A message to be sent along with the deletion message, by default None
        """

        if (prop == None):
            return
            
        message = (
            f"<delProperty "
            + f"device='{prop.get_device().get_name()}' "
            + f"name='{prop.get_name()}' "
            + f"timestamp='{get_timestamp()}'"
        )

        if msg is not None:
            message = message + f" message='{msg}'"

        message = message + ">\n"

        message = message + f"</delProperty>"
   
        self._send_message_to_client(message)

    def _send_message_to_client(self, message):
        print(str(message))

        #pp(str(message))
        sys.stdout.flush()
