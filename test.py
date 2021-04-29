def convert(timer):
    pos = ["m", "h", "d"]
    time_dict = {"m": 60, "h": 60 * 60, "d": 86400}
    unit = timer[-1]
    if unit not in pos:
        return -1
    try:
        val = int(timer[:-1])
    except:
        return -2
    return val * time_dict[unit]


print(f"30m: {convert('30m')}")
print(f"1h: {convert('1h')}")
print(f"2h: {convert('2h')}")
print(f"6h: {convert('6h')}")
print(f"12h: {convert('12h')}")
print(f"24h: {convert('24h')}")


