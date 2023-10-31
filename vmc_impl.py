from pythonosc import osc_message_builder, osc_message

class AbstractBlend (object):
    def __init__ (self, name: str):
        self.title = name
    
    def createBlendShapeMessage (self, value: float) -> osc_message.OscMessage:
        message = osc_message_builder.OscMessageBuilder(address="/VMC/Ext/Blend/Val")
        message.add_arg(self.title)
        message.add_arg(value)
        return message.build()
    
    def getMessage (self) -> osc_message.OscMessage:
        return self.createBlendShapeMessage(404)

class ToggleBlend (AbstractBlend):
    def __init__ (self, name: str, minValue: float, maxValue: float):
        super().__init__(name)
        self.state = False
        self.minValue = minValue
        self.maxValue = maxValue
    
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
        super().__init__(name)
        self.currentValue = minValue
        self.step = step
        self.minValue = minValue
        self.maxValue = maxValue
    
    def get (self) -> float:
        return self.currentValue
    
    def set (self, newValue: float) -> None:
        self.currentValue = newValue

    def getMessage (self) -> osc_message.OscMessage:
        return self.createBlendShapeMessage(self.get())

class DurationBlend (AbstractBlend):
    def __init__(self, name: str, progression:dict, offValue:float):
        super().__init__(name)
        pairs = [(int(i), float(progression[i])) for i in progression]
        pairs.sort(key=lambda x: x[0])

        self.index = 0
        self.values = []
        self.offValue = offValue

        for i in range(len(pairs)):
            currentCheckpoint = pairs[i-1]
            nextCheckpoint = pairs[i]
            steps = nextCheckpoint[0] - currentCheckpoint[0]
            if i == 0:
                currentCheckpoint = pairs[i]
                steps = currentCheckpoint[0]
            
            steps = max(steps, 1)
            
            stepSize = (nextCheckpoint[1] - currentCheckpoint[1]) / steps
            for j in range(steps):
                if j == steps - 1 or len(self.values) == 0:
                    self.values.append(nextCheckpoint[1])
                else:
                    self.values.append(self.values[-1] + stepSize)
    
    def get (self) -> float:
        if self.index < 0:
            return self.offValue
        else:
            return self.values[self.index]
    
    def step (self) -> bool:
        self.index += 1

        if self.index >= len(self.values):
            self.index = -1
            return False
        return True

def createBlendApplyMessage ():
    message = osc_message_builder.OscMessageBuilder(address="/VMC/Ext/Blend/Apply")
    return message.build()