def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


def get_hex(tk, color):
    rgb = tk.winfo_rgb(color)
    hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0] // 256, rgb[1] // 256, rgb[2] // 256)
    return hex_color
