from pythonosc import osc_server, dispatcher
def handle_velocity(addr, velocity):
    print(velocity)

disp = dispatcher.Dispatcher()
disp.map("/results", handle_velocity)

server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 5005), disp)
print("Waiting for Max analysis results...")
server.serve_forever()

