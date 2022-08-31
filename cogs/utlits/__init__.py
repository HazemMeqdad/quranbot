
times = {1800: "30m", 3600: "1h", 7200: "2h",
             21600: "6h", 43200: "12h", 86400: "24h"}

def convert_number_to_000(number: int) -> str:
    if number < 10:
        return "00" + str(number)
    elif number < 100:
        return "0" + str(number)
    else:
        return str(number)

def between_two_numbers(num: int, a: int, b: int):
    """
    True if the number is between the two numbers, False if not
    """
    if a < num and num < b: 
        return True
    else: 
        return False
