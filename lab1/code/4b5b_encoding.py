# -*- coding: utf-8 -*-
"""
Логическое кодирование 4B/5B исходного сообщения «ААД» (hex: C0 C0 C4).
После 4B/5B применяется физическое кодирование (выбран NRZ — обоснование в отчёте).
C = 100 Мбит/с или 1 Гбит/с.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Исходное сообщение (то же, что во всех предыдущих отчётах)
HEX_BYTES = [0xC0, 0xC0, 0xC4]  # "ААД"

# Стандартная таблица 4B/5B (IEEE 802.3 / FDDI): 4 бита данных → 5 бит кода
TABLE_4B5B = {
    0b0000: 0b11110,
    0b0001: 0b01001,
    0b0010: 0b10100,
    0b0011: 0b10101,
    0b0100: 0b01010,
    0b0101: 0b01011,
    0b0110: 0b01110,
    0b0111: 0b01111,
    0b1000: 0b10010,
    0b1001: 0b10011,
    0b1010: 0b10110,
    0b1011: 0b10111,
    0b1100: 0b11010,
    0b1101: 0b11011,
    0b1110: 0b11100,
    0b1111: 0b11101,
}

def bytes_to_bits_msb(bytes_list):
    bits = []
    for b in bytes_list:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def encode_4b5b(bits):
    """Логическое кодирование 4B/5B: по 4 бита → 5 бит."""
    if len(bits) % 4 != 0:
        raise ValueError("Длина битовой последовательности должна быть кратна 4")
    encoded = []
    for i in range(0, len(bits), 4):
        nibble = (bits[i] << 3) | (bits[i+1] << 2) | (bits[i+2] << 1) | bits[i+3]
        code5 = TABLE_4B5B[nibble]
        for j in range(4, -1, -1):
            encoded.append((code5 >> j) & 1)
    return encoded

def bits_to_hex(bits):
    """Биты (MSB first) → строка hex (дополняем слева нулями до кратного 4)."""
    n = len(bits)
    pad = (4 - n % 4) % 4
    if pad:
        bits = [0] * pad + bits
    h = []
    for i in range(0, len(bits), 4):
        nib = (bits[i] << 3) | (bits[i+1] << 2) | (bits[i+2] << 1) | bits[i+3]
        h.append(f"{nib:X}")
    return " ".join(h)

def nrz_encode(bits):
    """NRZ: 0 → -1, 1 → +1 (для диаграммы)."""
    t, v = [], []
    for i, b in enumerate(bits):
        level = 1 if b else -1
        t.extend([i, i + 1])
        v.extend([level, level])
    return np.array(t), np.array(v)

def max_run_length(bits):
    best, cur = 1, 1
    for i in range(1, len(bits)):
        if bits[i] == bits[i - 1]:
            cur += 1
        else:
            best = max(best, cur)
            cur = 1
    return max(best, cur)

def main():
    # --- Исходное сообщение ---
    bits_orig = bytes_to_bits_msb(HEX_BYTES)
    n_orig = len(bits_orig)
    print("Исходное сообщение: ААД")
    print("Hex (исходное):     ", bits_to_hex(bits_orig))
    print("Двоичный (исходное):", "".join(str(b) for b in bits_orig))
    print("Длина исходного:    ", n_orig, "бит")

    # --- Логическое кодирование 4B/5B ---
    bits_enc = encode_4b5b(bits_orig)
    n_enc = len(bits_enc)
    print("\n--- После логического кодирования 4B/5B ---")
    print("Двоичный (4B/5B):   ", "".join(str(b) for b in bits_enc))
    print("Hex (4B/5B):        ", bits_to_hex(bits_enc))
    print("Длина нового:       ", n_enc, "бит")

    # --- Избыточность ---
    # Избыточность = (L_new - L_orig) / L_new  или  (n_enc - n_orig) / n_enc
    redundancy = (n_enc - n_orig) / n_enc
    print("Избыточность:       ", f"{(n_enc - n_orig)} бит ({redundancy:.2%})")

    # --- Временная диаграмма (физическое кодирование — NRZ) ---
    t, v = nrz_encode(bits_enc)
    fig, ax = plt.subplots(figsize=(14, 3))
    ax.step(t, v, where='post', color='#1f77b4', linewidth=1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([-1, 1])
    ax.set_yticklabels(['Низкий', 'Высокий'])
    ax.set_xlabel('Время (биты канала после 4B/5B), 1 ед. = 1 бит')
    ax.set_ylabel('Уровень сигнала')
    ax.set_title('4B/5B + NRZ: «ААД» (C0 C0 C4) — временная диаграмма')
    n_bits = n_enc
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.set_xticklabels(['0', '5', '10', '15', '20', '25', '30'])
    ax.grid(True, axis='x', alpha=0.5)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    for x in range(1, n_bits):
        ax.axvline(x, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    plt.savefig('d:/itmo/seti/4b5b_nrz_diagram.png', dpi=150, bbox_inches='tight')
    print("\nВременная диаграмма сохранена: 4b5b_nrz_diagram.png")

    # --- Частотные характеристики для канала 100 Мбит/с и 1 Гбит/с ---
    for C_name, C_Mbps in [("100 Мбит/с", 100), ("1 Гбит/с", 1000)]:
        C_MHz = C_Mbps  # в формулах C в МГц
        n = max_run_length(bits_enc)
        f_v = C_MHz / 2
        f_n = C_MHz / (2 * n)
        f_half = (f_v + f_n) / 2
        f_sr = (10 * (f_v/2) + 3 * (f_v/3) + 5 * (f_v/5) + 6 * (f_v/6)) / 24  # как для NRZ
        S = f_v - f_n
        F = f_v  # полоса от 0 до f_в
        print("\n" + "="*60)
        print(f"Канал C = {C_name} (после 4B/5B + NRZ, n_бит = {n_enc}, макс. серия n = {n})")
        print("="*60)
        print(f"Верхняя граница частот:     f_в = C/2 = {f_v} МГц")
        print(f"Нижняя граница частот:     f_н = C/(2n) = {f_n:.2f} МГц")
        print(f"Середина спектра:           f_1/2 = (f_в+f_н)/2 = {f_half:.2f} МГц")
        print(f"Средняя частота:            f_ср = {f_sr:.2f} МГц (формула NRZ)")
        print(f"Спектр сигнала:             S = f_в - f_н = {S:.2f} МГц")
        print(f"Полоса пропускания:         F = {F} МГц (от 0 до f_в)")

    # --- Сравнение с исходным NRZ (без 4B/5B) при C = 100 Мбит/с ---
    print("\n--- Сравнение с исходным физическим кодом NRZ (без 4B/5B) при C = 100 Мбит/с ---")
    n_orig_run = max_run_length(bits_orig)
    f_v_orig = 50
    f_n_orig = 100 / (2 * n_orig_run)
    S_orig = f_v_orig - f_n_orig
    f_n_100 = 100 / (2 * n)
    S_100 = 50 - f_n_100
    print(f"Исходное (только NRZ): {n_orig} бит, макс. серия n = {n_orig_run}, S = {S_orig:.2f} МГц")
    print(f"После 4B/5B + NRZ:     {n_enc} бит, макс. серия n = {n}, S = {S_100:.2f} МГц")
    print("Вывод: 4B/5B ограничивает длинные серии (в 5-битных кодах не более 3 нулей подряд) → f_н выше.")

if __name__ == "__main__":
    main()
