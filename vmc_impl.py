from pythonosc import osc_message_builder, osc_message

class AbstractBlend (object):
    def __init__ (self, name: str, minValue: float, maxValue: float):
        self.title = name
        self.minValue = minValue
        self.maxValue = maxValue
    
    def createBlendShapeMessage (self, value: float) -> osc_message.OscMessage:
        message = osc_message_builder.OscMessageBuilder(address="/VMC/Ext/Blend/Val")
        message.add_arg(self.title)
        message.add_arg(value)
        return message.build()
    
    def getMessage (self) -> osc_message.OscMessage:
        return self.createBlendShapeMessage(404)

class ToggleBlend (AbstractBlend):
    def __init__ (self, name: str, minValue: float, maxValue: float):
        super().__init__(name, minValue, maxValue)
        self.state = False
    
    def toggle (self) -> None:
        self.state = not self.state
    
    def get (self) -> float:
        if self.state:
            return self.maxValue
        else:
            return self.minValue
        
    def getMessage (self) -> osc_message.OscMessage:
        return self.createBlendShapeMessage(self.get())

class SliderBlend (AbstractBlend):
    def __init__ (self, name: str, minValue: float, maxValue: float, step: float):
        super().__init__(name, minValue, maxValue)
        self.currentValue = minValue
        self.step = step
    
    def get (self) -> float:
        return self.currentValue
    
    def set (self, newValue: float) -> None:
        self.currentValue = newValue

    def getMessage (self) -> osc_message.OscMessage:
        return self.createBlendShapeMessage(self.get())


def createBlendApplyMessage ():
    message = osc_message_builder.OscMessageBuilder(address="/VMC/Ext/Blend/Apply")
    return message.build()