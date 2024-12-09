## Hardware

- Raspberry Pi 5
- USB camera

## OS

> raspios-bookworm-armhf-lite

## Setup:

1. Configure X11 Forwarding

```
$ sudo apt install x11-apps
```

2. Export display

```
$ export DISPLAY=localhost:10.0
```

3. Install dependencies

```
$ xargs -a requirements.txt sudo apt-get install -y
```

4. Run program

```
$ python main.py
```
