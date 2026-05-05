import ctypes
import signal
from ctypes import wintypes
from time import sleep

from function.main import generalMainMenu
from rich.console import Console

console = Console()
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

pid = 0
hprocess = None

hConsole = kernel32.GetStdHandle(-11)

byteDigits = {
    '0': 0x0, '1': 0x1, '2': 0x2, '3': 0x3,
    '4': 0x4, '5': 0x5, '6': 0x6, '7': 0x7,
    '8': 0x8, '9': 0x9, 'A': 0xA, 'B': 0xB,
    'C': 0xC, 'D': 0xD, 'E': 0xE, 'F': 0xF
}

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", wintypes.DWORD),
        ("hModule", wintypes.HMODULE),
        ("szModule", ctypes.c_char * 256),
        ("szExePath", ctypes.c_char * 260),
    ]

def is_running(proc_id):
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == -1:
        return False

    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(pe)

    result = False
    if kernel32.Process32First(snapshot, ctypes.byref(pe)):
        while True:
            if pe.th32ProcessID == proc_id:
                result = True
                break
            if not kernel32.Process32Next(snapshot, ctypes.byref(pe)):
                break

    kernel32.CloseHandle(snapshot)
    return result

def process_id_to_name(proc_id):
    handle = kernel32.OpenProcess(0x1000, False, proc_id)
    if not handle:
        return ""

    buffer = ctypes.create_unicode_buffer(1024)
    size = wintypes.DWORD(1024)
    result = ""

    if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
        result = buffer.value

    kernel32.CloseHandle(handle)
    return result

def get_module_info(module_name, proc_id):
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000008 | 0x00000010, proc_id)
    if snapshot == -1:
        return (None, None)

    me = MODULEENTRY32()
    me.dwSize = ctypes.sizeof(me)

    if not kernel32.Module32First(snapshot, ctypes.byref(me)):
        kernel32.CloseHandle(snapshot)
        return (None, None)

    result = (None, None)
    while kernel32.Module32Next(snapshot, ctypes.byref(me)):
        if me.szModule.decode('utf-8', errors='ignore').lower() == module_name.lower():
            result = (me.modBaseAddr, me.modBaseSize)
            break

    kernel32.CloseHandle(snapshot)
    return result

def attach_process():
    global pid, hprocess

    hwnd = user32.FindWindowW(None, "Among Us")
    if hwnd:
        pid_ptr = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_ptr))
        pid = pid_ptr.value

        hprocess = kernel32.OpenProcess(0x1F0FFF, False, pid)
        if hprocess:
            gamepath = process_id_to_name(pid)
            gameprocessname = gamepath[gamepath.rfind('\\') + 1:]
            console.log(f"已发现进程 [cornflower_blue]{gameprocessname}[/cornflower_blue]，PID 为 {pid}。")
            if gameprocessname.lower() == "among us.exe":
                return True
            else:
                console.log("[red1]进程校验失败[/red1]，似乎找到的进程不是 Among Us。")
        else:
            err = kernel32.GetLastError()
            console.log(f"[red1]操作失败[/red1]：未能获取程序句柄，错误码：{err}")
    return False

def signature_scan(base, sig, scan_size):
    search = []
    i = 0
    while i < len(sig):
        if sig[i] == ' ':
            i += 1
            continue
        if sig[i] == '?':
            search.append((0x0, True))
            if i + 1 < len(sig) and sig[i + 1] != '?':
                i -= 1
        else:
            high = byteDigits.get(sig[i].upper(), 0)
            low = byteDigits.get(sig[i + 1].upper(), 0) if i + 1 < len(sig) else 0
            search.append(((high * 0x10) + low, False))
        i += 2

    if not search:
        return 0

    buffer_size = 0x500
    buffer = ctypes.create_string_buffer(buffer_size)
    bytes_read = ctypes.c_size_t()

    progress = 0
    cached_progress = 0

    a = 0
    while a < scan_size:
        curr_scan_size = min(scan_size - a, buffer_size)
        if not kernel32.ReadProcessMemory(hprocess, base + a, buffer, curr_scan_size, ctypes.byref(bytes_read)) or bytes_read.value != curr_scan_size:
            return 0

        data = buffer.raw[:curr_scan_size]
        b = 0
        while b < curr_scan_size:
            if search[progress][1] or data[b] == search[progress][0]:
                if progress == 0:
                    cached_progress = b + 1
                progress += 1
            elif progress > 0:
                b = cached_progress
                progress = 0
                continue

            if progress >= len(search):
                return base + a + b - (len(search) - 1)
            b += 1
        a += buffer_size

    return 0

def patch_bytes(address, bytes_str):
    patch = []
    i = 0
    while i < len(bytes_str):
        if bytes_str[i] == ' ':
            i += 1
            continue
        high = byteDigits.get(bytes_str[i].upper(), 0)
        low = byteDigits.get(bytes_str[i + 1].upper(), 0) if i + 1 < len(bytes_str) else 0
        patch.append((high * 0x10) + low)
        i += 2

    if not patch:
        return False

    old_protect = wintypes.DWORD()
    if not kernel32.VirtualProtectEx(hprocess, address, len(patch), 0x40, ctypes.byref(old_protect)):
        return False

    patch_success = 0
    for i, byte_val in enumerate(patch):
        written = ctypes.c_size_t()
        if kernel32.WriteProcessMemory(hprocess, address + i, ctypes.byref(ctypes.c_ubyte(byte_val)), 1, ctypes.byref(written)) and written.value == 1:
            patch_success += 1

    kernel32.VirtualProtectEx(hprocess, address, len(patch), old_protect, None)
    return patch_success == len(patch)

pageText = """
此功能违反了 Innersloth 的服务条款，使用该功能可能导致账号被封禁。
如果你有能力购买饰品，请支持 Innersloth。
该功能通过内存注入实现，每次启动游戏时都需要重新破解。
"""

def cosmetic_unlock(for_old_version: bool = False):
    GALoaded = False
    GameAssemblyNp = 0
    GameAssemblySize = 0
    menuTitle = "皮肤解锁器"
    if for_old_version:
        menuTitle += " (Among Us v2022.10.15 - v16.0.5)"
    else:
        menuTitle += " (Among Us v16.1.0+)"
    generalMainMenu(pageText=pageText, title=menuTitle)
    original_handler = signal.getsignal(signal.SIGINT)
    def interrupt_handler(sig, frame):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGINT, interrupt_handler)

    try:
        console.log("可按下 [plum1]Ctrl+C[/plum1] 以取消操作。")
        with console.status("正在等待游戏启动...") as status:
            applied_patches = False
            if not attach_process():
                while True:
                    if attach_process():
                        break
                    sleep(0.1)

            status.update("进行进程校验...")
            if is_running(pid):
                status.update("等待 GameAssembly.dll 加载...")
                while(not GALoaded):
                    mod_info = get_module_info("GameAssembly.dll", pid)
                    if mod_info[0] and mod_info[1]:
                        GameAssemblyNp = ctypes.addressof(mod_info[0].contents)
                        GameAssemblySize = mod_info[1]

                        console.log(f"[green1]已找到 GameAssembly.dll 地址[/green1]: 0x{GameAssemblyNp:X}")
                        GALoaded = True

                        check = ctypes.c_ubyte()
                        if not kernel32.ReadProcessMemory(hprocess, GameAssemblyNp + 0x20, ctypes.byref(check), 1, None):
                            console.log("[orange1]读取内存失败[/orange1]，无法检测注入状态。")
                        elif check.value == 0x69:
                            console.log("检测到该进程[orange1]已被注入[/orange1]，无需重复操作。")
                            applied_patches = True
                    else:
                        sleep(0.1)
                if not applied_patches:
                    status.update("扫描 GameAssembly.dll ...")
                    scan_addr = GameAssemblyNp

                    if for_old_version:
                        curr_scan_addr = signature_scan(scan_addr, "74 05 B0 01 5E 5D C3 ?? ?? ?? ?? ?? F6", GameAssemblySize - (scan_addr - GameAssemblyNp))
                    else:
                        curr_scan_addr = signature_scan(scan_addr, "80 7E ?? 00 74 05 B0 01 5E 5D C3", GameAssemblySize - (scan_addr - GameAssemblyNp))

                    if curr_scan_addr > 0x100:
                        if not for_old_version:
                            curr_scan_addr += 4
                        scan_addr = curr_scan_addr
                        console.log("[green1]扫描成功[/green1]，已找到注入点。")
                        if not patch_bytes(scan_addr, "90 90"):
                            console.log("[red1]补丁失败[/red1]！发生未知错误。")
                            console.log("这可能是因为解锁器不支持该版本，或已有其他程序注入游戏。")
                            status.stop()
                            raise
                    else:
                        console.log("[red1]扫描失败[/red1]！未能找到注入点。")
                        console.log("这可能是因为解锁器不支持该版本，或已有其他程序注入游戏。")
                        status.stop()
                        raise

                    console.log("[green1]皮肤解锁完成[/green1]。")
                    patch_bytes(GameAssemblyNp + 0x20, "69")
                status.stop()
                console.input("按 [plum1]Enter[/plum1] 返回主菜单...")
                return
            else:
                console.log("[red1]进程校验失败[/red1]。这可能是因为游戏进程已关闭，或是其他程序意外与 Among Us 进程重名。")
                status.stop()
                raise
    except KeyboardInterrupt:
        status.stop()
        console.log("[orange1]已取消操作[/orange1]，即将返回主菜单。")
        sleep(1)
    except Exception:
        console.log("[red1]皮肤解锁失败[/red1]。")
        console.input("按 [plum1]Enter[/plum1] 返回主菜单...")
    finally:
        signal.signal(signal.SIGINT, original_handler)
