# -*- coding: utf-8 -*-
"""
AMI (Alternate Mark Inversion) — потенциальный код без возврата к нулю.
Кодирование "ААД" (hex: C0 C0 C4): 0 = нулевой уровень, 1 = поочерёдно +1 и -1, уровень держится весь такт.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HEX_BYTES = [0xC0, 0xC0, 0xC4]

def bytes_to_bits_msb_first(bytes_list):
    bits = []
    for b in bytes_list:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def max_run_zeros(bits):
    """Максимальная длина серии подряд идущих нулей (для AMI — уровень 0)."""
    if not bits:
        return 0
    best, cur = 0, 0
    for b in bits:
        if b == 0:
            cur += 1
        else:
            best = max(best, cur)
            cur = 0
    return max(best, cur)

def ami_encode(bits):
    """AMI: 0 → 0; 1 → чередование +1 и -1. Без возврата к нулю в середине такта (уровень на весь такт)."""
    signal_t = []
    signal_v = []
    t = 0.0
    T_bit = 1.0
    next_one = 1   # следующий "1" кодируем как +1
    for bit in bits:
        if bit == 0:
            level = 0
        else:
            level = next_one
            next_one = -next_one
        signal_t.extend([t, t + T_bit])
        signal_v.extend([level, level])
        t += T_bit
    return np.array(signal_t), np.array(signal_v)

def main():
    bits = bytes_to_bits_msb_first(HEX_BYTES)
    n_bits = len(bits)
    bit_str = ''.join(str(b) for b in bits)
    print("Исходное сообщение: ААД")
    print("Hex: C0 C0 C4")
    print(f"Биты (MSB first): {bit_str}")
    print(f"Всего бит: {n_bits}")

    t, v = ami_encode(bits)

    fig, ax = plt.subplots(figsize=(14, 3))
    ax.step(t, v, where='post', color='#1f77b4', linewidth=1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(['−1', '0', '+1'])
    ax.set_xlabel('Время (нормированные единицы, 1 ед. = 1 бит)')
    ax.set_ylabel('Уровень сигнала')
    ax.set_title('AMI (без возврата к нулю): "ААД" (C0 C0 C4)')
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_xticklabels(['0', '4', '8', '12', '16', '20', '24'])
    ax.grid(True, axis='x', alpha=0.5)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    for x in range(1, n_bits):
        ax.axvline(x, color='gray', linestyle='--', linewidth=0.7, alpha=0.8)
    for i in range(n_bits):
        ax.annotate(str(bits[i]), xy=(i + 0.5, 1.3), ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('d:/itmo/seti/ami_signal.png', dpi=150, bbox_inches='tight')
    print("\nГрафик сохранён: ami_signal.png")

    # --- Спектр AMI по тем же правилам ---
    # f_в: теоретический максимум при чередовании 1 и 0 (или +1 и -1) → период 2 такта → f_в = C/2
    # f_н: нет DC; при длинной серии нулей — f_н = C/(2n); если нулей подряд нет — f_н = C/2
    C_MHz = 100
    n_zeros = max_run_zeros(bits)
    f_v = C_MHz / 2                      # 50 МГц — при чередовании (как NRZ)
    f_n = C_MHz / (2 * n_zeros) if n_zeros > 0 else C_MHz / 2
    n = n_zeros if n_zeros > 0 else None
    f_half = (f_v + f_n) / 2
    f_sr = (30 * f_v + 18 * f_n) / 48
    S = f_v - f_n
    F = f_v - f_n

    print("\n" + "="*60)
    print("Параметры спектра AMI (C = 100 Мбит/с)")
    print("По формулам: f_в = C/2, f_н = C/(2n), n — макс. серия нулей (уровень 0)")
    print("="*60)
    print(f"Макс. серия нулей:           n = {n_zeros}" + (f"  → f_н = C/{2*n_zeros}" if n_zeros else "  → f_н = C/2 (типичный минимум)"))
    print(f"Верхняя граница частот:     f_в = C/2 = {f_v} МГц  (чередование 1-0 или +1,-1)")
    print(f"Нижняя граница частот:     f_н = " + (f"C/(2n) = {f_n:.2f} МГц  (период 2n тактов)" if n_zeros else f"C/2 = {f_n} МГц  (нет DC)"))
    print(f"Середина спектра:           f_1/2 = (f_в+f_н)/2 = {f_half:.2f} МГц")
    print(f"Средняя частота:            f_ср = (30*f_в + 18*f_н)/48 = {f_sr:.2f} МГц")
    print(f"Ширина спектра:             S = f_в - f_н = {S:.2f} МГц")
    print(f"Полоса пропускания:         F = f_в - f_н = {F:.2f} МГц  (от f_н до f_в, без DC)")
    print("\n--- Что за что отвечает ---")
    print("f_в = C/2 — теоретический максимум при чередовании (период = 2 такта), как у NRZ.")
    print("f_н = C/(2n) — определяется самой длинной серией нулей (постоянный уровень 0). Нет DC.")
    print("S = F = f_в - f_н — ширина спектра и полоса пропускания.")

if __name__ == "__main__":
    main()
