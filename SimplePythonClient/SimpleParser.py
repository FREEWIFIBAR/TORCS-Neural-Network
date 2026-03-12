class SimpleParser(object):

    def __init__(self):
        pass

    def stringify(self, tag, value):

        STR = "("
        STR = STR + str(tag)

        # If value is a list iterate through the list
        if type(value) == type(list()):
            for v in value:
                STR = STR + " " + str(v)
        else:
            STR = STR + " " + str(value)

        STR = STR + ")"
        return STR

    def parse(self, sensors, tag):
        # Values to return
        values = []

        # Remove first and last bracket
        sensors = sensors[1:len(sensors) - 1]

        # Split in list containing strings between ( )
        listSensors = sensors.split(")(")

        for l in listSensors:
            entry = l.split(" ")

            if entry[0] == tag:
                # Remove tag
                del entry[0]

                # Create list of values
                for v in entry:
                    values.append(float(v))

        return values
