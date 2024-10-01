class ColorConverter:
    @staticmethod
    def rgb_to_hsv(r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        v = cmax

        s = 0 if cmax == 0 else delta / cmax

        if delta == 0:
            h = 0
        elif cmax == r:
            h = (60 * ((g - b) / delta) + 360) % 360
        elif cmax == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        elif cmax == b:
            h = (60 * ((r - g) / delta) + 240) % 360

        return round(h), round(s * 100), round(v * 100)
        
    @staticmethod
    def cmyk_to_rgb(c, m, y, k):
        r = round(255 * (1 - c / 100.0) * (1 - k / 100.0))
        g = round(255 * (1 - m / 100.0) * (1 - k / 100.0))
        b = round(255 * (1 - y / 100.0) * (1 - k / 100.0))

        return r, g, b

    @staticmethod
    def hsv_to_rgb(h, s, v):
        h /= 60.0
        s /= 100.0
        v /= 100.0

        hi = int(h) % 6
        f = h - int(h)

        m = v * (1 - s)
        n = v * (1 - f * s)
        k = v * (1 - (1 - f) * s)

        match hi:
            case 0: return round(v * 255), round(k * 255), round(m * 255)
            case 1: return round(n * 255), round(v * 255), round(m * 255)
            case 2: return round(m * 255), round(v * 255), round(k * 255)
            case 3: return round(m * 255), round(n * 255), round(v * 255)
            case 4: return round(k * 255), round(m * 255), round(v * 255)
            case 5: return round(v * 255), round(m * 255), round(n * 255)

    @staticmethod
    def rgb_to_cmyk(r, g, b):
        k = min(1 - r / 255.0, 1 - g / 255.0, 1 - b / 255.0)
        c = (1 - r / 255.0 - k) / (1 - k) if (1 - k) != 0 else 0
        m = (1 - g / 255.0 - k) / (1 - k) if (1 - k) != 0 else 0
        y = (1 - b / 255.0 - k) / (1 - k) if (1 - k) != 0 else 0

        return round(c * 100), round(m * 100), round(y * 100), round(k * 100)