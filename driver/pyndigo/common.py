"""
This module contain the basic classes upon which INDIGO clients, drivers 
and agents are built. Particularly they encapsulate the logic for 
Properties and Items.

Classes
-------
:obj:`~pyndigo.common.PyndigoItem`
    An item which can be contained into a 
    :obj:`~pyndigo.common.PyndigoProperty`. This is where the
    values for the properties are really stored.

:obj:`~pyndigo.common.PyndigoProperty`
    An INDIGO Property to store one or more items. They have a 
    particular type (Text, Number, Switch, Light, Blob)

Constants
---------
STATE_OK
    ``Ok`` State for a :obj:`~pyndigo.common.PyndigoProperty`.
STATE_BUSY
    ``Busy`` State for a :obj:`~pyndigo.common.PyndigoProperty`.
STATE_ALERT
    ``Alert`` State for a :obj:`~pyndigo.common.PyndigoProperty`.
STATE_IDLE
    ``Idle`` State for a :obj:`~pyndigo.common.PyndigoProperty`.
LIGHT_OK
    ``Ok`` value for a light :obj:`~pyndigo.common.PyndigoItem`.
LIGHT_BUSY
    ``Busy`` value for a light :obj:`~pyndigo.common.PyndigoItem`.
LIGHT_ALERT
    ``Alert`` value for a light :obj:`~pyndigo.common.PyndigoItem`.
LIGHT_IDLE
    ``Idle`` value for a light :obj:`~pyndigo.common.PyndigoItem`.
TYPE_TEXT
    Type ``Text`` for a :obj:`~pyndigo.common.PyndigoProperty` or a 
    :obj:`~pyndigo.common.PyndigoItem`.
TYPE_NUMBER
    Type ``Number`` for a :obj:`~pyndigo.common.PyndigoProperty` or a 
    :obj:`~pyndigo.common.PyndigoItem`.
TYPE_SWITCH
    Type ``Switch`` for a :obj:`~pyndigo.common.PyndigoProperty` or a 
    :obj:`~pyndigo.common.PyndigoItem`.
TYPE_LIGHT
    Type ``Light`` for a :obj:`~pyndigo.common.PyndigoProperty` or a 
    :obj:`~pyndigo.common.PyndigoItem`.
TYPE_BLOB
    Type ``BLOB`` for a :obj:`~pyndigo.common.PyndigoProperty` or a 
    :obj:`~pyndigo.common.PyndigoItem`.
RULE_ONE_OF_MANY 
    Rule ``OneOfMany`` for a switch 
    :obj:`~pyndigo.common.PyndigoProperty`.
RULE_AT_MOST_ONE
    Rule ``AtMostOne`` for a switch 
    :obj:`~pyndigo.common.PyndigoProperty`.
RULE_ANY_OF_MANY
    Rule ``AnyOfMany`` for a switch 
    :obj:`~pyndigo.common.PyndigoProperty`.
SWITCH_ON
    Switch value ``On`` for a :obj:`~pyndigo.common.PyndigoItem`.
SWITCH_OFF
    Switch value ``Off`` for a :obj:`~pyndigo.common.PyndigoItem`.
PERM_RW
    Permissions ``rw`` (read / write) for a 
    :obj:`~pyndigo.common.PyndigoProperty`.
PERM_RO = "ro"
    Permissions ``ro`` (read only) for a 
    :obj:`~pyndigo.common.PyndigoProperty`.
PERM_WO = "wo"
    Permissions ``wo`` (write only) for a 
    :obj:`~pyndigo.common.PyndigoProperty`.
"""
import base64
from .utils import get_timestamp
from .utils import print_msg as pp

STATE_OK = "Ok"
STATE_BUSY = "Busy"
STATE_ALERT = "Alert"
STATE_IDLE = "Idle"

LIGHT_OK = "Ok"
LIGHT_BUSY = "Busy"
LIGHT_ALERT = "Alert"
LIGHT_IDLE = "Idle"

TYPE_TEXT = "Text"
TYPE_NUMBER = "Number"
TYPE_SWITCH = "Switch"
TYPE_LIGHT = "Light"
TYPE_BLOB = "BLOB"

RULE_ONE_OF_MANY = "OneOfMany"
RULE_AT_MOST_ONE = "AtMostOne"
RULE_ANY_OF_MANY = "AnyOfMany"

SWITCH_ON = "On"
SWITCH_OFF = "Off"

PERM_RW = "rw"
PERM_RO = "ro"
PERM_WO = "wo"


class PyndigoItem:
    """
    An item which can be contained into a 
    :obj:`~pyndigo.common.PyndigoProperty`. This is where the
    values for the properties are really stored.

    Usually these objects are not created with the class constructor:

    * If you develop a Client, the Properties and Items will be
      automatically created when the Property is received from the
      Server.

    * If you develop a Driver, you should create the Items using the
      methods:

        * :obj:`PyndigoProperty.add_text(...)
          <pyndigo.common.PyndigoProperty.add_text>`
        * :obj:`PyndigoProperty.add_number(...)
          <pyndigo.common.PyndigoProperty.add_number>`
        * :obj:`PyndigoProperty.add_switch(...)
          <pyndigo.common.PyndigoProperty.add_switch>`
        * :obj:`PyndigoProperty.add_light(...)
          <pyndigo.common.PyndigoProperty.add_light>`
        * :obj:`PyndigoProperty.add_blob(...)
          <pyndigo.common.PyndigoProperty.add_blob>`
    """

    def __init__(
        self,
        parent_property: "PyndigoProperty",
        name: str = None,
        value=None,
        label: str = "",
        number_format: str = None,
        min_value=None,
        max_value=None,
        step=None,
        hints: str = None,
        blob_format: str = None,
        _decoded_json=None,
    ):
        """
        Constructs a new :obj:`~pyndigo.common.PyndigoItem`.
        If you are developing an INDIGO Client, an INDIGO Driver or an
        agent you **MUST NOT** use this constructor.
        """

        self._property = parent_property
        self._size = 0
        self._blob_format = ""
        self._format = None
        self._min = None
        self._max = None
        self._step = None
        self._url = None
        self._target = None
        self._hints = None


        if _decoded_json is None:
            self._name = name
            self._label = label
            self._value = value
            self._hints = hints

            if parent_property.is_number():
                self._format = number_format
                self._min = min_value
                self._max = max_value
                self._step = step

            if parent_property.is_blob():
                self._blob_format = blob_format
        else:
            self._name = _decoded_json.get("name")
            self._label = _decoded_json.get("label")
            self._value = _decoded_json.get("value")
            self._hints = _decoded_json.get("hints")

            if parent_property.is_number():
                self._format = _decoded_json.get("format")
                self._min = _decoded_json.get("min")
                self._max = _decoded_json.get("max")
                self._step = _decoded_json.get("step")

            if parent_property.is_blob():
                self._blob_format = _decoded_json.get("format")

    def _update(self, _decoded_json):
        self._value = _decoded_json.get("value")

        if self._property.is_BLOB():
            self._size = _decoded_json.get("size")
            self._blob_format = _decoded_json.get("format")
            self._url = _decoded_json.get("url")

        if self._property.is_number():
            self._target = _decoded_json.get("target")

    def _get_def_xml(self):
        message = (
            f"  <def{self.get_property().get_type()} "
            + f"name='{self.get_name()}' label='{self.get_label()}'"
        )

        if self.get_hints() is not None:
            message = message + f" hints='{self.get_hints()}'"

        if self.get_property().is_number():
            message = (
                message
                + f" format='{self.get_format()}' min='{self.get_min()}'"
                + f" max='{self.get_max()}' step='{self.get_step()}'"
            )

        message = (
            message + f">{self.get_value()}</def{self.get_property().get_type()}>\n"
        )

        #pp(message)
        return message

    def _get_one_xml(self):
        message = (
            f"  <one{self.get_property().get_type()} name='{self.get_name()}'"
        )

        if self.get_property().is_blob():
            message = (
                message + f" size='{str(self.get_size())}' format='{self.get_blob_format()}'"
            )

        message = (
            message + f">{self.get_value()}</one{self.get_property().get_type()}>\n"
        )

 
        return message

    def get_property(self) -> "PyndigoProperty":
        """Gets the parent property to which the item belongs.

        Returns
        -------
        PyndigoProperty
            The parent property to which the item belongs.
        """
        return self._property

    def get_name(self) -> str:
        """Gets the name of the item. Usually UPPERCASE_UNDERSCORED.

        Returns
        -------
        str
            The name of the item.
        """
        return self._name

    def get_label(self) -> str:
        """Gets the label of the item (usually used in GUIs).

        Returns
        -------
        str
            The label of the item.
        """
        return self._label

    def get_value(self):
        """Gets the value of the item.

        Returns
        -------
        str or number
            The value of the item. For text, switch, light and blob
            items it returns a ``str``. For number items it may return a
            number or ``str`` (depending on the format).
        """
        return self._value

    def set_value(self, value):
        """Sets the value of the item. If you are developing a Client,
        you **MUST NOT** use this method. You should use...

        Parameters
        ----------
        value : str or number
            The value to be set on the item. Use only when developing a
            Driver.
        """

        if isinstance(value, bytes):
            self._size = len(value)
            value = base64.b64encode(value).decode('ascii')

        self._value = value

    def get_type(self) -> str:
        """Gets the type of the item.

        Returns
        -------
        str
            One of :obj:`~pyndigo.common.TYPE_TEXT`,
            :obj:`~pyndigo.common.TYPE_NUMBER`,
            :obj:`~pyndigo.common.TYPE_SWITCH`,
            :obj:`~pyndigo.common.TYPE_LIGHT` or
            :obj:`~pyndigo.common.TYPE_BLOB`
        """
        return self._property.get_type()

    def __str__(self):
        return str(self._name) + " [" + str(self._label) + "]: " + str(self._value)

    def get_format(self) -> str:
        """Gets the **format** for the Number
        :obj:`~pyndigo.common.PyndigoItem`.

        Returns
        -------
        str
            The **format** for the Number
            :obj:`~pyndigo.common.PyndigoItem`. If it is of
            a different type, returns ``None``.
        """
        if self.get_property().is_number():
            return self._format

        return None

    def get_min(self):
        """Gets the **minimum** for the Number
        :obj:`~pyndigo.common.PyndigoItem`.

        Returns
        -------
        str
            The **minimum** for the Number
            :obj:`~pyndigo.common.PyndigoItem`. If it is of
            a different type, returns ``None``.
        """
        if self.get_property().is_number():
            return self._min

        return None

    def get_max(self):
        """Gets the **maximum** for the Number
        :obj:`~pyndigo.common.PyndigoItem`.

        Returns
        -------
        str
            The **maximum** for the Number
            :obj:`~pyndigo.common.PyndigoItem`. If it is of
            a different type, returns ``None``.
        """
        if self.get_property().is_number():
            return self._max

        return None

    def get_step(self):
        """Gets the **step** for the Number
        :obj:`~pyndigo.common.PyndigoItem`.

        Returns
        -------
        str
            The **step** for the Number
            :obj:`~pyndigo.common.PyndigoItem`. If it is of
            a different type, returns ``None``.
        """
        if self.get_property().is_number():
            return self._step

        return None

    def get_target(self):
        """Gets the **target** value for the Number
        :obj:`~pyndigo.common.PyndigoItem`.

        Returns
        -------
        str
            The **target** value for the Number
            :obj:`~pyndigo.common.PyndigoItem`. If it is of
            a different type, returns ``None``.
        """
        if self.get_property().is_number():
            return self._target

        return None

    def get_blob_format(self) -> str:
        """Gets the **format** for the BLOB
        :obj:`~pyndigo.common.PyndigoItem` data.

        Returns
        -------
        str
            The **format** for the BLOB
            :obj:`~pyndigo.common.PyndigoItem` data. If it is of
            a different type, returns ``None``.
        """
        if self.get_property().is_blob():
            return self._blob_format

        return None
    
    def set_blob_format(self, blob_format: str) -> None:
        if self.get_property().is_blob():
            self._blob_format = blob_format



    def get_size(self):
        """Gets the **size** for the BLOB
        :obj:`~pyndigo.common.PyndigoItem` data.

        Returns
        -------
        str
            The **size** for the BLOB
            :obj:`~pyndigo.common.PyndigoItem` data. If it
            is of a different type, returns ``0``.
        """
        if self.get_property().is_blob():
            return self._size

        return 0

    def get_url(self) -> str:
        """Gets the **URL** for the BLOB
        :obj:`~pyndigo.common.PyndigoItem` data.

        Returns
        -------
        str
            The **URL** for the BLOB
            :obj:`~pyndigo.common.PyndigoItem` data. If it
            is of a different type, returns ``None``.
        """
        if self.get_property().is_blob():
            return self._url

        return None

    def get_hints(self) -> str:
        """Gets the presentation **hints** for the
        :obj:`~pyndigo.common.PyndigoItem`.

        Returns
        -------
        str
            The representation **hints** for the
            :obj:`~pyndigo.common.PyndigoItem`.
        """
        return self._hints


class PyndigoProperty:
    """
    A property of a particular type
    (:obj:`~pyndigo.common.TYPE_TEXT`,
    :obj:`~pyndigo.common.TYPE_NUMBER`,
    :obj:`~pyndigo.common.TYPE_SWITCH`,
    :obj:`~pyndigo.common.TYPE_LIGHT` or
    :obj:`~pyndigo.common.TYPE_BLOB`).

    Usually these objects are not created with the class constructor:

    * If you develop a Client, the Properties and Items will be
      automatically created when the Property is received from the
      Server.

    * If you develop a Driver, you should create the Properties using
      the methods:

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
    """

    def __init__(
        self,
        device,
        prop_type: str,
        name: str = "",
        state: str = "",
        perm: str = "",
        label: str = "",
        group: str = "",
        timeout=0,
        timestamp: str = None,
        message: str = "",
        rule: str = None,
        hints=None,
        _decoded_json=None,
    ):
        """
        Constructs a new :obj:`~pyndigo.common.PyndigoProperty`.
        If you are developing an INDIGO Client, an INDIGO Driver or an
        agent you **MUST NOT** use this constructor.
        """
        self._device:PyndigoDevice = device

        self._type:str = prop_type
        self._items:dict[str, PyndigoItem] = {}

        if _decoded_json is None:
            self._name:str = name
            self._state:str = state
            self._label:str = label
            self._group:str = group
            self._timestamp:str = timestamp
            self._message:str = message
            self._hints:str = hints

            if self._type == TYPE_SWITCH:
                self._rule:str = rule

            if self._type == TYPE_LIGHT:
                self._timeout:int = 0
                self._perm:str = PERM_RO
            else:
                self._timeout:int = timeout
                self._perm:str = perm

        else:
            self._name:str = _decoded_json.get("name")
            self._state:str = _decoded_json.get("state")
            self._label:str = _decoded_json.get("label")
            self._group:str = _decoded_json.get("group")
            self._timestamp:str = _decoded_json.get("timestamp")
            self._message:str = _decoded_json.get("message")
            self._hints:str = _decoded_json.get("hints")

            if self._type == TYPE_SWITCH:
                self._rule:str = _decoded_json.get("rule")

            if self._type == TYPE_LIGHT:
                self._timeout:int = 0
                self._perm:str = PERM_RO
            else:
                self._timeout:int = _decoded_json.get("timeout")
                self._perm:str = _decoded_json.get("perm")

            # Procesing items
            items = _decoded_json.get("items")

            for i in items:
                # Also gets added to this property
                PyndigoItem(parent_property=self, _decoded_json=i)

    def _update(self, _decoded_json):
        self._state = _decoded_json.get("state")
        self._timestamp = _decoded_json.get("timestamp")
        self._message = _decoded_json.get("message")

        if self._type != TYPE_LIGHT:
            self._timeout = _decoded_json.get("timeout")

        # Procesing items
        items = _decoded_json.get("items")

        for i in items:
            item = self.get_item(i.get("name"))

            item._update(_decoded_json=i)

    def _get_def_xml(self):
        message = (
            f"<def{self.get_type()}Vector "
            + f"device='{self.get_device().get_name()}' "
            + f"name='{self.get_name()}' group='{self.get_group()}' "
            + f"label='{self.get_label()}' state='{self.get_state()}'"
        )

        if not self.is_light():
            message = (
                message
                + f" perm='{self.get_perm()}' "
                + f"timeout='{self.get_timeout()}'"
            )

        if self.is_switch():
            message = message + f" rule='{self.get_rule()}'"

        if self.get_hints() is not None:
            message = message + f"hints='{self.get_hints()}'"

        message = message + ">\n"

        for i in self.get_items().values():
            message = message + i._get_def_xml()

        message = message + f"</def{self.get_type()}Vector>\n"

        return message

    def _get_set_xml(self, msg: str = None):
        message = (
            f"<set{self.get_type()}Vector "
            + f"device='{self.get_device().get_name()}' "
            + f"name='{self.get_name()}' state='{self.get_state()}' "
            + f"timestamp='{get_timestamp()}'"
        )

        if msg is not None:
            message = message + f" message='{msg}'"

        message = message + ">\n"

        for i in self.get_items().values():
            message = message + i._get_one_xml()

        message = message + f"</set{self.get_type()}Vector>"

        return message

    def add_text(
        self, name: str, value: str, label: str = None, hints: str = None
    ) -> "PyndigoProperty":
        """
        Adds a new Text Item to the Property

        Parameters
        ----------
        name : str
            The name of the property. Usually UPPERCASE_UNDERSCORED
        value : str
            The initial value for the property
        label : str, optional
            A readable name for the property, usually used in GUIs, by
            default None
        hints : str, optional
            Some hints to format the GUI for the new text item. Check
            INDIGO docs for more details, by default None

        Returns
        -------
        PyndigoProperty
            The Property itself (in case of need chaining calls)
        """

        pi = PyndigoItem(self, name=name, value=value, label=label, hints=hints)
        self._add_item(pi)

        return self

    def add_number(
        self,
        name: str,
        value: str,
        number_format: str,
        min_value,
        max_value,
        step,
        label: str = None,
        hints: str = None,
    ) -> "PyndigoProperty":
        """
        Adds a new Number Item to the Property

        Parameters
        ----------
        name : str
            The name of the property. Usually UPPERCASE_UNDERSCORED
        value : str
            The initial value for the property
        number_format : str
            The number format description of the item. Check INDI White
            paper for more details
        min_value : number or str
            Minimum value for the property
        max_value : number or str
            Maximum value for the property
        step : number or str
            Steps (increments) for the value, by default 1
        label : str, optional
            A readable name for the property, usually used in GUIs, by
            default None
        hints : str, optional
            Some hints to format the GUI for the new text item. Check
            INDIGO docs for more details, by default None

        Returns
        -------
        PyndigoProperty
            The Property itself (in case of need chaining calls)
        """

        pi = PyndigoItem(
            self,
            name=name,
            value=value,
            number_format=number_format,
            min_value=min_value,
            max_value=max_value,
            step=step,
            label=label,
            hints=hints,
        )
        self._add_item(pi)

        return self

    def add_switch(
        self,
        name: str,
        value: str,
        label: str = None,
        hints: str = None,
    ) -> "PyndigoProperty":
        """
        Adds a new Switch Item to the Property

        Parameters
        ----------
        name : str
            The name of the property. Usually UPPERCASE_UNDERSCORED
        value : str
            The initial value for the property
        label : str, optional
            A readable name for the property, usually used in GUIs, by
            default None
        hints : str, optional
            Some hints to format the GUI for the new text item. Check
            INDIGO docs for more details, by default None

        Returns
        -------
        PyndigoProperty
            The Property itself (in case of need chaining calls)
        """

        pi = PyndigoItem(
            self,
            name=name,
            value=value,
            label=label,
            hints=hints,
        )
        self._add_item(pi)

        return self

    def add_light(
        self,
        name: str,
        value: str,
        label: str = None,
        hints: str = None,
    ) -> "PyndigoProperty":
        """
        Adds a new Light Item to the Property

        Parameters
        ----------
        name : str
            The name of the property. Usually UPPERCASE_UNDERSCORED
        value : str
            The initial value for the property
        label : str, optional
            A readable name for the property, usually used in GUIs, by
            default None
        hints : str, optional
            Some hints to format the GUI for the new text item. Check
            INDIGO docs for more details, by default None

        Returns
        -------
        PyndigoProperty
            The Property itself (in case of need chaining calls)
        """

        pi = PyndigoItem(
            self,
            name=name,
            value=value,
            label=label,
            hints=hints,
        )
        self._add_item(pi)

        return self

    def add_blob(
        self,
        name: str,
        value: str,
        blob_format: str = "",
        label: str = None,
        hints: str = None,
    ) -> "PyndigoProperty":
        """
        Adds a new BLOB Item to the Property

        Parameters
        ----------
        name : str
            The name of the property. Usually UPPERCASE_UNDERSCORED.
        value : str
            The initial value for the property
        blob_format: str
            The format of the BLOB item. Default ""
        label : str, optional
            A readable name for the property, usually used in GUIs, by
            default None
        hints : str, optional
            Some hints to format the GUI for the new text item. Check
            INDIGO docs for more details, by default None

        Returns
        -------
        PyndigoProperty
            The Property itself (in case of need chaining calls)
        """

        pi = PyndigoItem(
            self,
            name=name,
            value=value,
            blob_format=blob_format,
            label=label,
            hints=hints,
        )
        self._add_item(pi)

        return self

    def _add_item(self, item):
        self._items[item.get_name()] = item

    def get_item(self, item_name:str) -> PyndigoItem:
        """Gets the :obj:`~pyndigo.common.PyndigoItem` with a given name.

        Parameters
        ----------
        item_name : str
            The name of the item

        Returns
        -------
        PyndigoItem
            The item with the given name. ``None`` if there is no
            item with this name in the property.
        """
        return self._items.get(item_name)

    def get_items(self) -> dict[str, PyndigoItem]:
        """
        Get the Items of this Property.

        Returns
        -------
        dict[str, PyndigoItem]
            A dictionary with the Items of the Property. keys = name of 
            the property and value = the property. 
        """
        return self._items.copy()

    def get_type(self) -> str:
        """
        Gets the type of the property.

        Returns
        -------
        str
            One of :obj:`~pyndigo.common.TYPE_TEXT`,
            :obj:`~pyndigo.common.TYPE_NUMBER`,
            :obj:`~pyndigo.common.TYPE_SWITCH`,
            :obj:`~pyndigo.common.TYPE_LIGHT` or
            :obj:`~pyndigo.common.TYPE_BLOB`.
        """

        return self._type

    def is_text(self) -> bool:
        """
        Checks if the property is of :obj:`~pyndigo.common.TYPE_TEXT`.

        Returns
        -------
        bool
            ``True`` if the property type is 
            :obj:`~pyndigo.common.TYPE_TEXT`.

            ``False`` otherwise.
        """
        return self._type == TYPE_TEXT

    def is_number(self) -> bool:
        """
        Checks if the property is of :obj:`~pyndigo.common.TYPE_NUMBER`.

        Returns
        -------
        bool
            ``True`` if the property type is 
            :obj:`~pyndigo.common.TYPE_NUMBER`.

            ``False`` otherwise.
        """
        return self._type == TYPE_NUMBER

    def is_switch(self) -> bool:
        """
        Checks if the property is of :obj:`~pyndigo.common.TYPE_SWITCH`.

        Returns
        -------
        bool
            ``True`` if the property type is 
            :obj:`~pyndigo.common.TYPE_SWITCH`.

            ``False`` otherwise.
        """
        return self._type == TYPE_SWITCH

    def is_light(self) -> bool:
        """
        Checks if the property is of :obj:`~pyndigo.common.TYPE_LIGHT`.

        Returns
        -------
        bool
            ``True`` if the property type is 
            :obj:`~pyndigo.common.TYPE_LIGHT`.

            ``False`` otherwise.
        """
        return self._type == TYPE_LIGHT

    def is_blob(self) -> bool:
        """
        Checks if the property is of :obj:`~pyndigo.common.TYPE_BLOB`.

        Returns
        -------
        bool
            ``True`` if the property type is 
            :obj:`~pyndigo.common.TYPE_BLOB`.

            ``False`` otherwise.
        """
        return self._type == TYPE_BLOB

    def is_ok(self) -> bool:
        """
        Checks if the property state is :obj:`~pyndigo.common.STATE_OK`.

        Returns
        -------
        bool
            ``True`` if the property state is 
            :obj:`~pyndigo.common.STATE_OK`.

            ``False`` otherwise.
        """
        return self._state == STATE_OK

    def is_busy(self) -> bool:
        """
        Checks if the property state is :obj:`~pyndigo.common.STATE_BUSY`.

        Returns
        -------
        bool
            ``True`` if the property state is 
            :obj:`~pyndigo.common.STATE_BUSY`.

            ``False`` otherwise.
        """
        return self._state == STATE_BUSY


    def is_alert(self) -> bool:
        """
        Checks if the property state is :obj:`~pyndigo.common.STATE_ALERT`.

        Returns
        -------
        bool
            ``True`` if the property state is 
            :obj:`~pyndigo.common.STATE_ALERT`.

            ``False`` otherwise.
        """
        return self._state == STATE_ALERT

    def is_idle(self) -> bool:
        """
        Checks if the property state is :obj:`~pyndigo.common.STATE_IDLE`.

        Returns
        -------
        bool
            ``True`` if the property state is 
            :obj:`~pyndigo.common.STATE_IDLE`.

            ``False`` otherwise.
        """
        return self._state == STATE_IDLE

    def set_ok(self) -> None:
        """
            Sets the state of the property as 
            :obj:`~pyndigo.common.STATE_OK`.

            Do not use for Clients development, just for Drivers. 
        """
        self._state = STATE_OK

    def set_busy(self) -> None:
        """
            Sets the state of the property as 
            :obj:`~pyndigo.common.STATE_BUSY`.

            Do not use for Clients development, just for Drivers. 
        """
        self._state = STATE_BUSY

    def set_alert(self) -> None:
        """
            Sets the state of the property as 
            :obj:`~pyndigo.common.STATE_ALERT`.

            Do not use for Clients development, just for Drivers. 
        """
        self._state = STATE_ALERT

    def set_idle(self) -> None:
        """
            Sets the state of the property as 
            :obj:`~pyndigo.common.STATE_IDLE`.

            Do not use for Clients development, just for Drivers. 
        """
        self._state = STATE_IDLE

    def get_name(self) -> str:
        """Gets the **name** of the property. Usually UPPERCASE_UNDERSCORED.

        Returns
        -------
        str
            The **name** of the property.
        """
        return self._name

    def get_state(self) -> str:
        """
        Gets the **state** of the property.

        Returns
        -------
        str
            The **state** of the property. That is, one of 
            :obj:`~pyndigo.common.STATE_OK`,
            :obj:`~pyndigo.common.STATE_BUSY`,
            :obj:`~pyndigo.common.STATE_ALERT` or
            :obj:`~pyndigo.common.STATE_IDLE`.
        """
        return self._state

    def _set_state(self, state) -> None:
        self._state = state
        
    def get_perm(self) -> str:
        """
        Gets the **permissions** of the property.

        Returns
        -------
        str
            The **permissions** of the property, that is, one of
            :obj:`pyndigo.common.PERM_RW`, :obj:`pyndigo.common.PERM_RO`
            or :obj:`pyndigo.common.PERM_WO`.
        """
        return self._perm

    def is_read_write(self) -> bool:
        """
        Checks if the permission of the property is 
        :obj:`pyndigo.common.PERM_RW`.

        Returns
        -------
        bool
            ``True`` if the property permission is 
            :obj:`pyndigo.common.PERM_RW`.

            ``False`` otherwise.
        """
        return self._perm == PERM_RW

    def is_read_only(self) -> bool:
        """
        Checks if the permission of the property is 
        :obj:`pyndigo.common.PERM_RO`.

        Returns
        -------
        bool
            ``True`` if the property permission is 
            :obj:`pyndigo.common.PERM_RO`.

            ``False`` otherwise.
        """
        return self._perm == PERM_RO

    def is_write_only(self) -> bool:
        """
        Checks if the permission of the property is 
        :obj:`pyndigo.common.PERM_WO`.

        Returns
        -------
        bool
            ``True`` if the property permission is 
            :obj:`pyndigo.common.PERM_WO`.

            ``False`` otherwise.
        """
        return self._perm == PERM_WO

    def get_label(self) -> str:
        """Gets the **label** of the property (usually used in GUIs).

        Returns
        -------
        str
            The **label** of the property.
        """
        return self._label

    def get_group(self) -> str:
        """Gets the **group** of the property.

        Returns
        -------
        str
            The **group** of the property.
        """
        return self._group

    def get_timeout(self):
        """Gets the **timeout** of the property.

        Returns
        -------
        str
            The **timeout** of the property.
        """
        return self._timeout

    def get_timestamp(self):
        """Gets the **timestamp** of the property.

        Returns
        -------
        str
            The **timestamp** of the property.
        """
        return self._timestamp

    def get_last_message(self) -> str:
        """Gets the last **message** of the property.

        Returns
        -------
        str
            The last **message** of the property.
        """
        return self._message

    def get_rule(self) -> str:
        """Gets the **rule** of the property.

        Returns
        -------
        str
            The **rule** of the property. That is, one of 
            :obj:`pyndigo.common.RULE_ONEOFMANY`,
            :obj:`pyndigo.common.RULE_ATMOSTONE`,
            :obj:`pyndigo.common.RULE_ANYOFMANY`.
        """
        return self._rule

    def get_hints(self) -> str:
        """Gets the **hints** of the property.

        Returns
        -------
        str
            The **hints** of the property.
        """
        return self._hints

    def get_device(self) -> "PyndigoDevice":
        """Gets the **device** of the property.

        Returns
        -------
        str
            The **device** of the property.
        """
        return self._device

    def __str__(self):
        temp = (
            str(self._name)
            + " ["
            + str(self._label)
            + "] ("
            + self._type
            + ") ["
            + str(self._state)
            + "] ["
            + str(self._perm)
            + "] "
        )

        if self._group != "" and self._group is not None:
            temp = temp + "[G: " + str(self._group) + "] "

        if self.is_switch():
            temp = temp + str(self._rule) + " "

        return temp


class PyndigoDevice:
    def __init__(self, name):
        self._name = name
        self._properties = {}
        self._timestamp = 0
        self._message = ""

    def _update_message(self, timestamp, message):
        self._timestamp = timestamp
        self._message = message

    def add_property(self, prop: PyndigoProperty):
        self._properties[prop.get_name()] = prop

    def remove_property(
        self, property_name: str, timestamp: str = None, message: str = None
    ):
        if property_name in self._properties:
            self._properties.pop(property_name)
            self._timestamp = timestamp
            self._message = message

            print("Removing property " + property_name)

    def get_properties(self) -> dict:
        return self._properties.copy()

    def get_property(self, propertyName) -> PyndigoProperty:
        return self._properties.get(propertyName)

    def get_name(self) -> str:
        return self._name

    def get_timestamp(self):
        return self._timestamp

    def get_message(self) -> str:
        return self._message
