def __formula_grey_m(position_percent):
    # Fórmula para Grey-M Multivoltas
    return int((position_percent / 100) * 65535)

def __formula_grey_q(position_percent):
    # Fórmula para Grey-Q Evolution
    # Suponhamos que este use uma escala diferente
    return int((position_percent / 100) * 255)

def __formula_white_e(position_percent):
    # Fórmula para White-E Evolution
    # Este poderia ter um valor mínimo de 103 (0x67) e máximo de 104 (0x68)
    return int((position_percent / 100) * 1000)

def __formula_top_e(position_percent):
    # Fórmula para TOP-E Module
    # Este tem range de 0x7CF a 0xBB7 (1999 a 3000)
    min_val = 1999
    max_val = 2999
    return min_val + int((position_percent / 100) * (max_val - min_val))

actuators_data = {
    "Grey-M Multivoltas": {"address": 0x01, "data_open": 0xFF, "data_close": 0x00, "formula": __formula_grey_m},
    "Grey-Q Evolution": {"address": 0x00, "data_open": 0x00, "data_close": 0x00, "formula": __formula_grey_q},
    "White-E Evolution": {"address": 0x0B, "data_open": 0x68, "data_close": 0x67, "formula": __formula_white_e},
    "TOP-E Module": {"address": 0x01, "data_open": 0xBB7, "data_close": 0x7CF, "formula": __formula_top_e},
}