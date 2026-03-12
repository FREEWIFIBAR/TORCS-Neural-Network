import SimplePythonClient.CarControl as CarControl
import SimplePythonClient.CarState as CarState
import numpy as np
import onnxruntime as ort

class tstage:
    WARMUP = 0
    QUALIFYING = 1
    RACE = 2
    UNKNOWN = 3

class Piloto(object):

    stage = tstage()
    trackName = ""
    gearUp = [5000, 6000, 6000, 6500, 7000, 0]
    gearDown = [0, 2500, 3000, 3000, 3500, 3500]

    def __init__(self):
        print("Iniciando Piloto con IA")
        self.stuckCounter = 0
        self.bringingCartBack = 0

        self.sess_gear  = ort.InferenceSession('IA_gear.onnx')
        self.sess_steer = ort.InferenceSession('IA_steer.onnx')
        self.sess_accel = ort.InferenceSession('IA_accel.onnx')

        self.in_gear  = self.sess_gear.get_inputs()[0].name
        self.in_steer = self.sess_steer.get_inputs()[0].name
        self.in_accel = self.sess_accel.get_inputs()[0].name

        self.scaler_mean = np.array([
            0.00424124, -0.03587277, 0.34076363, 87.81081956, 4478.02652870, 3.07992081, 8.85218519, 9.22173950, 10.46321119, 13.98068459, 32.79043061, 42.62312353, 45.08685176, 48.56330786, 54.11960027, 60.54193851, 53.57177223, 43.87459227, 35.97234715, 29.78835747, 16.81455592, 11.16968290, 8.68768589, 7.77306994, 7.51026690
        ], dtype=np.float32)

        self.scaler_scale = np.array([
            0.07751773, 0.39780542, 0.00643658, 39.02597825, 915.19491354, 1.19861751, 5.91656852, 6.19044757, 7.13277275, 12.34460280, 39.71116455, 41.17919216, 40.72477930, 41.90474806, 45.94119062, 52.45119681, 49.08837869, 40.16797528, 31.08608718, 26.57504666, 11.78866256, 7.76804924, 4.99218481, 4.47188906, 4.32812363
        ], dtype=np.float32)

    def init(self, angles):
        # Initialization of the desired angles for the rangefinders
        i = 0
        for i in range(0, len(angles)):
            angles[i] = -90 + i * 10

    # The main function:
    #     - the input variable sensors represents the current world sate
    #     - it returns a string representing the controlling action to perform
    def Update(self, buffer):

        sensors = CarState.CarState(buffer)
        
        state = []
        state.append(sensors.getAngle())
        state.append(sensors.getTrackPos())
        state.append(sensors.getZ()[0])
        state.append(sensors.getSpeedX())
        state.append(sensors.getRpm())
        state.append(sensors.getGear())

        state.append(sensors.getTracks()[0])
        state.append(sensors.getTracks()[1])
        state.append(sensors.getTracks()[2])
        state.append(sensors.getTracks()[3])
        state.append(sensors.getTracks()[4])
        state.append(sensors.getTracks()[5])
        state.append(sensors.getTracks()[6])
        state.append(sensors.getTracks()[7])
        state.append(sensors.getTracks()[8])
        state.append(sensors.getTracks()[9])
        state.append(sensors.getTracks()[10])
        state.append(sensors.getTracks()[11])
        state.append(sensors.getTracks()[12])
        state.append(sensors.getTracks()[13])
        state.append(sensors.getTracks()[14])
        state.append(sensors.getTracks()[15])
        state.append(sensors.getTracks()[16])
        state.append(sensors.getTracks()[17])
        state.append(sensors.getTracks()[18])

        sensor_vector = np.array(state, dtype=np.float32)
        sensor_norm = (sensor_vector - self.scaler_mean) / self.scaler_scale
        onnx_input = sensor_norm.reshape(1, -1)

        pred_gear = self.sess_gear.run(None, {self.in_gear: onnx_input})[0][0][0]
        pred_steer = self.sess_steer.run(None, {self.in_steer: onnx_input})[0][0][0]
        pred_pedales = self.sess_accel.run(None, {self.in_accel: onnx_input})[0][0]

        gear = int(np.clip(np.round(pred_gear), 1, 6))
        steer = np.clip(pred_steer, -1.0, 1.0)
        accel = np.clip(pred_pedales[0], 0.0, 1.0)
        brake = np.clip(pred_pedales[1], 0.0, 1.0)
        
        action = CarControl.CarControl(gear=gear, steer=steer, accel=accel, brake=brake, clutch=0, meta=0, focus=0)
        return str(action)

    def getInitAngles(self):
        return [-90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

    # Function called at shutdown
    def onShutdown(self):
        print("Bye bye!")

    # Function called at server restart
    def onRestart(self):
        print("Restarting the race!")