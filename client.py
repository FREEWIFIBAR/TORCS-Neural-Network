import socket
import time
import datetime
import SimplePythonClient.Piloto as Piloto
import SimplePythonClient.SimpleParser as SimpleParser

SERVER_IP = "127.0.0.1"
CLIENT_PORT = 3002

# Maximal size of file read from socket
BUFSIZE = 1024

# Set default values
maxEpisodes = 0
maxSteps = 100000
serverPort = 3001
hostName = "localhost"
id = "championship2011"
stage = Piloto.tstage.WARMUP
trackName = "unknown"

#    noise=false
#    noiseAVG=0
#    noiseSTD=0.05
#    seed=0

class client():
    def __init__(self, driver):
        self.timeoutCounter = 0
        self.driver = driver

    def run(self):
        # Bind client to UDP-Socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", CLIENT_PORT))

        print("***********************************")
        print("HOST: ", hostName)
        print("PORT: ", serverPort)
        print("ID: ", id)
        print("MAX_STEPS: ", maxSteps)
        print("MAX_EPISODES: ", maxEpisodes)
        print("TRACKNAME: ", trackName)

        if stage == Piloto.tstage.WARMUP:
            print("STAGE: WARMUP")
        elif Piloto.tstage.QUALIFYING:
            print("STAGE:QUALIFYING")
        elif Piloto.tstage.RACE:
            print("STAGE: RACE")
        else:
            print("STAGE: UNKNOWN")

        driver = self.driver
        sp = SimpleParser.SimpleParser()
        driver.stage = stage

        shutdownClient = False
        msg_in = ""

        while True:
            # Initialize the angles of rangefinders
            angles = driver.getInitAngles()

            # driver.init(angles);
            initString = sp.stringify("init", angles)
            # print("Sending id to server: ", id
            initString = str(id) + initString
            # print("Sending init string to the server: ", initString)
            s.sendto((initString.encode()), (SERVER_IP, serverPort))

            # Read data from socket
            try:
                # Wait to connect to server, without sleep program freezes
                time.sleep(0.2)
                msg_in, (client_ip, client_port) = s.recvfrom(BUFSIZE)

                msg_in = msg_in.decode()

                # print(client_ip, " ", client_port, " received:", msg_in[:-1])  # do not print last character "\00"

                # Remove last character from string, seems to be a new line
                msg_in = msg_in[:-1]

                if msg_in == "***identified***":
                    break
            except:
                print("no server running")

        currentStep = 0
        # Connected to server
        while True:
            try:
                msg_in, (client_ip, client_port) = s.recvfrom(BUFSIZE)

                msg_in = msg_in.decode()

                # recTime = time.clock()
                recTime = datetime.datetime.now()
                # print("[", recTime, "]", client_ip, " ", client_port, " message received; length = ", len(msg_in))
                # Remove last character from string, could be a new line character
                msg_in = msg_in[:-1]

            except:
                print("error connection lost")

            if msg_in == "***shutdown***":
                driver.onShutdown()
                shutdownClient = True
                print("Client Shutdown")
                break

            if msg_in == "***restart***":
                driver.onRestart()
                print("Client Restart")
                break

            # ***************************************************
            # Compute The Action to send to the solo race server
            # ***************************************************
            currentStep = currentStep + 1
            if currentStep != maxSteps:
                action = driver.Update(msg_in)

                # Write action to buffer
                print("sending action", action)

                # Create correct format
                msgBuffer = action
            else:
                # Max actions reached
                msgBuffer = "(meta 1)"

            # Send action
            s.sendto(msgBuffer.encode(), (SERVER_IP, serverPort))


if __name__ == '__main__':
    # Import your driver
    import SimplePythonClient.Piloto as Piloto

    driver = Piloto.Piloto()
    myclient = client(driver)
    myclient.run()
