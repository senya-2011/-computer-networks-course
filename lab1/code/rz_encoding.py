# -*- coding: utf-8 -*-
"""
RZ – Биполярный импульсный код с возвратом к нулю.

Принцип: 1 — высокий уровень (+1) в первой половине такта, во второй половине — ноль;
         0 — низкий уровень (−1) в первой половине такта, во второй половине — ноль.

(Спектр: f_в=C, f_н=C/2, f_ср = (30·f_в + 18·f_н)/48, как у манчестера.)
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

def rz_encode_bipolar(bits):
    """RZ биполярный: 1 → +1 затем 0; 0 → −1 затем 0 (возврат к нулю в каждой второй половине такта)."""
    signal_t = []
    signal_v = []
    t = 0.0
    T_bit = 1.0
    T_half = T_bit / 2
    for bit in bits:
        pulse = 1 if bit else -1
        signal_t.extend([t, t + T_half - 1e-9, t + T_half, t + T_bit])
        signal_v.extend([pulse, pulse, 0, 0])
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

    t, v = rz_encode_bipolar(bits)

    fig, ax = plt.subplots(figsize=(14, 3))
    ax.step(t, v, where='post', color='#1f77b4', linewidth=1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(['−1', '0', '+1'])
    ax.set_xlabel('Время (нормированные единицы, 1 ед. = 1 бит)')
    ax.set_ylabel('Уровень сигнала')
    ax.set_title('RZ (биполярный импульсный код с возвратом к нулю): "ААД" (C0 C0 C4)')
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_xticklabels(['0', '4', '8', '12', '16', '20', '24'])
    ax.grid(True, axis='x', alpha=0.5)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    for x in range(1, n_bits):
        ax.axvline(x, color='gray', linestyle='--', linewidth=0.7, alpha=0.8)
    for i in range(n_bits):
        ax.annotate(str(bits[i]), xy=(i + 0.5, 1.3), ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('d:/itmo/seti/rz_signal.png', dpi=150, bbox_inches='tight')
    print("\nГрафик сохранён: rz_signal.png")

    # --- Спектр RZ по формулам (как у другого человека): f_в=C, f_н=C/2, f_ср как у манчестера ---
    C_MHz = 100
    f_v = C_MHz                        # f_в = C = 100 МГц
    f_n = C_MHz / 2                    # f_н = C/2 = 50 МГц
    f_half = (f_v + f_n) / 2           # 75 МГц
    f_sr = (30 * f_v + 18 * f_n) / 48  # (30·f_в + 18·f_н)/48 = 81.25 МГц (как у манчестера)
    S = C_MHz / 2
    F = C_MHz / 2

    print("\n" + "="*60)
    print("Параметры спектра RZ (C = 100 Мбит/с)")
    print("По формулам: f_в = C, f_н = C/2, S = F = C/2, f_ср = (30·f_в + 18·f_н)/48")
    print("="*60)
    print(f"Верхняя граница частот:     f_в = C = {f_v} МГц")
    print(f"Нижняя граница частот:     f_н = C/2 = {f_n} МГц")
    print(f"Середина спектра:           f_1/2 = (f_в+f_н)/2 = {f_half} МГц")
    print(f"Средняя частота:            f_ср = (30·f_в + 18·f_н)/48 = {f_sr} МГц")
    print(f"Ширина спектра:             S = C/2 = {S} МГц")
    print(f"Полоса пропускания:         F = {F} МГц")
    print("\n--- Что за что отвечает ---")
    print("Биполярный RZ (как на графике): нет DC, границы спектра как у манчестера.")
    print("f_в = C, f_н = C/2, S = F = C/2. f_ср — та же формула (30·f_в + 18·f_н)/48.")

if __name__ == "__main__":
    main()
