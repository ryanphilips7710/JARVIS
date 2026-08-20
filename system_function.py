import os
import datetime
import psutil
import platform

apps = ['google', "code", "explorer", "spotify", "whatsapp:"]

def date_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")

    day= f"Today is {now.strftime('%A, %B %d, %Y')}."
    time= f"The current time is {current_time}."
    return day, time


def open_google():
    chrome_profile="Profile 5"
    url = "https://mail.google.com/mail/u/0/#inbox"
    url2 = "chrome://newtab/"
    try:
        os.system(f'start "" chrome --profile-directory="{chrome_profile}" --new-tab "{url}" "{url2}"')
    except Exception as e:
        pass

def open_app(app_name):
    app_name = app_name.lower()
    if app_name in apps:
        try:
            if app_name in ["google", "chrome"]:
                open_google()
            elif app_name == "whatsapp":
                os.system("start whatsapp:")
            else:
                os.system(f"start {app_name}")
            print(f"Opening {app_name}...")

        except Exception as e:
            print(f"Could not launch {app_name}: {e}")
    else:
        print(f"{app_name} is not in supported apps list.")
        

def get_system_info():
    print("=" * 50)
    print("         SYSTEM INFORMATION DASHBOARD")
    print("=" * 50)

    # ── CPU ──────────────────────────────────────────
    print("\n📊 CPU USAGE")
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count   = psutil.cpu_count(logical=False)
    cpu_logical = psutil.cpu_count(logical=True)
    cpu_freq    = psutil.cpu_freq()

    print(f"  Usage        : {cpu_percent}%")
    print(f"  Physical cores: {cpu_count}")
    print(f"  Logical cores : {cpu_logical}")
    if cpu_freq:
        print(f"  Frequency     : {cpu_freq.current:.0f} MHz  "
              f"(max: {cpu_freq.max:.0f} MHz)")

    # ── RAM ──────────────────────────────────────────
    print("\n💾 RAM USAGE")
    ram = psutil.virtual_memory()
    print(f"  Total     : {ram.total / 1e9:.2f} GB")
    print(f"  Used      : {ram.used  / 1e9:.2f} GB  ({ram.percent}%)")
    print(f"  Available : {ram.available / 1e9:.2f} GB")

    # ── DISK ─────────────────────────────────────────
    print("\n💿 DISK USAGE")
    disk = psutil.disk_usage('/')
    print(f"  Total : {disk.total / 1e9:.2f} GB")
    print(f"  Used  : {disk.used  / 1e9:.2f} GB  ({disk.percent}%)")
    print(f"  Free  : {disk.free  / 1e9:.2f} GB")

    # ── SYSTEM SPECS ─────────────────────────────────
    print("\n🖥️  SYSTEM SPECS")
    uname = platform.uname()
    print(f"  OS         : {uname.system} {uname.release}")
    print(f"  Version    : {uname.version}")
    print(f"  Machine    : {uname.machine}")
    print(f"  Processor  : {uname.processor}")
    print(f"  Node name  : {uname.node}")

    # ── BATTERY ──────────────────────────────────────
    print("\n🔋 BATTERY")
    battery = psutil.sensors_battery()
    if battery:
        status = "Charging ⚡" if battery.power_plugged else "Discharging 🔌"
        secs   = battery.secsleft
        if secs == psutil.POWER_TIME_UNLIMITED:
            time_left = "Fully charged / plugged in"
        elif secs == psutil.POWER_TIME_UNKNOWN:
            time_left = "Calculating..."
        else:
            time_left = str(datetime.timedelta(seconds=secs))

        print(f"  Percentage : {battery.percent:.1f}%")
        print(f"  Status     : {status}")
        print(f"  Time left  : {time_left}")
    else:
        print("  No battery detected (desktop PC?)")

    # ── UPTIME ───────────────────────────────────────
    print("\n⏱️  UPTIME")
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime    = datetime.datetime.now() - boot_time
    print(f"  Boot time : {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Uptime    : {str(uptime).split('.')[0]}")

    print("\n" + "=" * 50)


def get_system_summary():
    """Return a brief spoken summary of CPU and RAM usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_used = ram.used / 1e9
    ram_total = ram.total / 1e9
    ram_percent = ram.percent
    
    summary = f"CPU usage is at {cpu_percent} percent. RAM usage is {ram_used:.1f} gigabytes out of {ram_total:.1f}, which is {ram_percent} percent full."
    return summary