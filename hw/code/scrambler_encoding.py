# -*- coding: utf-8 -*-
"""
Этап 4. Скремблирование исходного сообщения «ААД» (hex: C0 C0 C4).
Полином 1: B_i = A_i ⊕ B_{i-3} ⊕ B_{i-5}
Полином 2: B_i = A_i ⊕ B_{i-5} ⊕ B_{i-7}
Выбран полином 1 (короче обратная связь, меньше задержка, достаточная рандомизация).
После скремблирования — физическое кодирование NRZ (как на этапе 3).
C = 100 Мбит/с или 1 Гбит/с.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HEX_BYTES = [0xC0, 0xC0, 0xC4]  # "ААД"

def bytes_to_bits_msb(bytes_list):
    bits = []
    for b in bytes_list:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def scramble_poly1(A):
    """Скремблирование: B_i = A_i ⊕ B_{i-3} ⊕ B_{i-5}. Начальные B_{i<0} = 0."""
    B = []
    for i in range(len(A)):
        b_3 = B[i - 3] if i >= 3 else 0
        b_5 = B[i - 5] if i >= 5 else 0
        B.append(A[i] ^ b_3 ^ b_5)
    return B

def scramble_poly2(A):
    """Скремблирование: B_i = A_i ⊕ B_{i-5} ⊕ B_{i-7}. Начальные B_{i<0} = 0."""
    B = []
    for i in range(len(A)):
        b_5 = B[i - 5] if i >= 5 else 0
        b_7 = B[i - 7] if i >= 7 else 0
        B.append(A[i] ^ b_5 ^ b_7)
    return B

def scramble_poly1_with_steps(A):
    """Возвращает (B, список строк пошагового вывода). Полином: B_i = A_i ⊕ B_{i-3} ⊕ B_{i-5}. Индексация с 1."""
    B = []
    lines = []
    for i in range(len(A)):
        idx = i + 1  # 1-based
        b_3 = B[i - 3] if i >= 3 else 0
        b_5 = B[i - 5] if i >= 5 else 0
        val = A[i] ^ b_3 ^ b_5
        B.append(val)
        a_val = A[i]
        if i < 3:
            expr = f"A_{idx}"
        elif i < 5:
            expr = f"A_{idx}⊕B_{idx-3}"
        else:
            expr = f"A_{idx}⊕B_{idx-3}⊕B_{idx-5}"
        lines.append(f"B_{idx}\t= {expr}\t= {val}")
    return B, lines

def bits_to_hex(bits):
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
    A = bytes_to_bits_msb(HEX_BYTES)
    n = len(A)
    orig_spaced = " ".join("".join(str(A[k]) for k in range(i, min(i+4, n))) for i in range(0, n, 4))
    print("Исходное сообщение: ААД")
    print("Исходное сообщение: ", orig_spaced)
    print("Hex (исходное):     ", bits_to_hex(A))
    print("Длина:              ", n, "бит")

    # Выбор полинома: для данной последовательности полином 1 даёт макс. серию 7 (хуже исходной 6) — берём полином 2, если у него серия меньше
    B1 = scramble_poly1(A)
    B2 = scramble_poly2(A)
    run1 = max_run_length(B1)
    run2 = max_run_length(B2)
    run_orig = max_run_length(A)
    use_poly2 = run2 < run1 or (run2 == run1 and run2 < run_orig)
    if use_poly2:
        B = B2
        print("\n--- Выбран полином 2: B_i = A_i ⊕ B_{i-5} ⊕ B_{i-7} ---")
        print("Обоснование: полином 1 даёт макс. серию n =", run1, ", полином 2 — n =", run2, ", исходная —", run_orig, ". Выбираем полином 2 (меньшая макс. серия).")
        steps = []
        for i in range(len(A)):
            idx = i + 1
            val = B[i]
            a_val = A[i]
            b_5 = B[i - 5] if i >= 5 else 0
            b_7 = B[i - 7] if i >= 7 else 0
            if i < 5:
                expr = f"A_{idx}"
            elif i < 7:
                expr = f"A_{idx}⊕B_{idx-5}"
            else:
                expr = f"A_{idx}⊕B_{idx-5}⊕B_{idx-7}"
            steps.append(f"B_{idx}\t= {expr}\t= {val}")
        poly_name = "B_i = A_i ⊕ B_{i-5} ⊕ B_{i-7}"
    else:
        B, steps = scramble_poly1_with_steps(A)
        print("\n--- Выбран полином 1: B_i = A_i ⊕ B_{i-3} ⊕ B_{i-5} ---")
        print("Обоснование: меньшая задержка обратной связи (3 и 5 тактов), проще реализация. Макс. серия n =", run1, ".")
        poly_name = "B_i = A_i ⊕ B_{i-3} ⊕ B_{i-5}"
    print("\n--- Пошаговый расчёт (индексация с 1) ---")
    for line in steps:
        print(line)

    print("\n--- Скремблированное сообщение ---")
    enc_spaced = " ".join("".join(str(B[k]) for k in range(i, min(i+4, len(B)))) for i in range(0, len(B), 4))
    print("Двоичный:           ", enc_spaced)
    print("Двоичный (подряд):  ", "".join(str(b) for b in B))
    print("Hex:                ", bits_to_hex(B))
    print("Длина:              ", len(B), "бит (без изменения)")
    n_run = max_run_length(B)
    print("Макс. серия одинаковых бит: n =", n_run, "(у исходного было", run_orig, ")")

    # Временная диаграмма (NRZ)
    t, v = nrz_encode(B)
    fig, ax = plt.subplots(figsize=(14, 3))
    ax.step(t, v, where='post', color='#1f77b4', linewidth=1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([-1, 1])
    ax.set_yticklabels(['Низкий', 'Высокий'])
    ax.set_xlabel('Время (биты), 1 ед. = 1 бит')
    ax.set_ylabel('Уровень сигнала')
    ax.set_title(f'Скремблирование ({poly_name}) + NRZ: «ААД» — временная диаграмма')
    n_bits = len(B)
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_xticklabels(['0', '4', '8', '12', '16', '20', '24'])
    ax.grid(True, axis='x', alpha=0.5)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    for x in range(1, n_bits):
        ax.axvline(x, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    plt.savefig('d:/itmo/seti/scrambler_nrz_diagram.png', dpi=150, bbox_inches='tight')
    print("\nВременная диаграмма сохранена: scrambler_nrz_diagram.png")

    # Частотные характеристики при C = 100 Мбит/с и 1 Гбит/с
    n_run = max_run_length(B)
    for C_name, C_MHz in [("100 Мбит/с", 100), ("1 Гбит/с", 1000)]:
        f_v = C_MHz / 2
        f_n = C_MHz / (2 * n_run)
        f_half = (f_v + f_n) / 2
        f_sr = (10 * (f_v/2) + 3 * (f_v/3) + 5 * (f_v/5) + 6 * (f_v/6)) / 24
        S = f_v - f_n
        F = f_v
        print("\n" + "="*60)
        print(f"Канал C = {C_name} (скремблирование + NRZ, макс. серия n = {n_run})")
        print("="*60)
        print(f"Верхняя граница частот:     f_в = C/2 = {f_v} МГц")
        print(f"Нижняя граница частот:     f_н = C/(2n) = {f_n:.2f} МГц")
        print(f"Середина спектра:           f_1/2 = (f_в+f_н)/2 = {f_half:.2f} МГц")
        print(f"Средняя частота:            f_ср = {f_sr:.2f} МГц")
        print(f"Спектр сигнала:             S = f_в - f_н = {S:.2f} МГц")
        print(f"Полоса пропускания:         F = {F} МГц (от 0 до f_в)")

    # Сравнение с исходным NRZ (без скремблирования) при C = 100 Мбит/с
    n_orig_run = max_run_length(A)
    f_n_orig = 100 / (2 * n_orig_run)
    S_orig = 50 - f_n_orig
    f_n_sc = 100 / (2 * n_run)
    S_sc = 50 - f_n_sc
    print("\n--- Сравнение с исходным физическим кодом NRZ (без скремблирования), C = 100 Мбит/с ---")
    print(f"Исходное (только NRZ): макс. серия n = {n_orig_run}, S = {S_orig:.2f} МГц")
    print(f"После скремблирования + NRZ: макс. серия n = {n_run}, S = {S_sc:.2f} МГц")
    print("Вывод: скремблирование (полином 2) сократило макс. серию с 6 до 5 → f_н выросла (8,33 → 10 МГц), спектр S = 40 МГц (исходный 41,67 МГц).")

if __name__ == "__main__":
    main()
