#!/usr/bin/env python

from pyndigo.driver import *

class FirstExampleDevice(PyndigoDriverDevice):
    def __init__(self, driver):
        super().__init__(driver, "First Example Device")

        prop = self.add_text_property(
            "TEST_TEXT",
            STATE_OK,
            PERM_RO,
            label="First text property",
            group="Test Properties",
        )
        prop.add_text("TEXT_1", "Hello World", label="First text item")

        prop = self.add_number_property(
            "TEST_NUMBER",
            STATE_OK,
            PERM_RW,
            label="First number property",
            group="Test Properties",
        )
        prop.add_number("SPEED", "10", number_format="%1.0f", min_value=0, max_value=100, step=1, label="Speed")
        prop.add_number("ACCEL", "1", number_format="%1.0f", min_value=0, max_value=100, step=1, label="Acceleration")



dr = PyndigoDriver("My driver")
dev = FirstExampleDevice(dr)
dr.read()
