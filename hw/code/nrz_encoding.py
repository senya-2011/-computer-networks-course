# -*- coding: utf-8 -*-
"""
NRZ (Non-Return to Zero) — потенциальный код без возврата к нулю.
Кодирование "ААД" (hex: C0 C0 C4): 0 = низкий уровень, 1 = высокий, уровень держится весь такт.
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

def max_run_length(bits):
    """Максимальная длина серии подряд идущих одинаковых бит."""
    if not bits:
        return 0
    best = 1
    cur = 1
    for i in range(1, len(bits)):
        if bits[i] == bits[i - 1]:
            cur += 1
        else:
            best = max(best, cur)
            cur = 1
    return max(best, cur)

def nrz_encode(bits):
    """NRZ: 0 → низкий (-1), 1 → высокий (+1), без возврата к нулю в середине такта."""
    signal_t = []
    signal_v = []
    t = 0.0
    T_bit = 1.0
    for bit in bits:
        level = 1 if bit else -1
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

    t, v = nrz_encode(bits)

    fig, ax = plt.subplots(figsize=(14, 3))
    ax.step(t, v, where='post', color='#1f77b4', linewidth=1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([-1, 1])
    ax.set_yticklabels(['Низкий', 'Высокий'])
    ax.set_xlabel('Время (нормированные единицы, 1 ед. = 1 бит)')
    ax.set_ylabel('Уровень сигнала')
    ax.set_title('NRZ (без возврата к нулю): "ААД" (C0 C0 C4)')
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_xticklabels(['0', '4', '8', '12', '16', '20', '24'])
    ax.grid(True, axis='x', alpha=0.5)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    for x in range(1, n_bits):
        ax.axvline(x, color='gray', linestyle='--', linewidth=0.7, alpha=0.8)
    for i in range(n_bits):
        ax.annotate(str(bits[i]), xy=(i + 0.5, 1.3), ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('d:/itmo/seti/nrz_signal.png', dpi=150, bbox_inches='tight')
    print("\nГрафик сохранён: nrz_signal.png")

    # --- Спектр NRZ по вашему отчёту ---
    # f_в: максимум при чередовании 1010 → период 2 такта → f_в = C/2
    # f_н: макс. серия одинаковых бит n → период 2n тактов → f_н = C/(2n)
    # Для "ААД" считаем n по фактической последовательности бит
    C_MHz = 100
    n = max_run_length(bits)
    f_v = C_MHz / 2                    # 50 МГц — при чередовании 1-0-1-0
    f_n = C_MHz / (2 * n)              # f_н = C/6 при n=3; для "ААД" n=6 → C/12
    f_half = (f_v + f_n) / 2
    # Для NRZ средняя частота — своя формула (не как у манчестера 30/18):
    # f_ср = (10·f_в/2 + 3·f_в/3 + 5·f_в/5 + 6·f_в/6) / 24
    f_sr = (10 * (f_v / 2) + 3 * (f_v / 3) + 5 * (f_v / 5) + 6 * (f_v / 6)) / 24
    S = f_v - f_n                      # ширина спектра S = f_в - f_н
    # Полоса пропускания: от 0 Гц (DC) до ≈ f_в

    print("\n" + "="*60)
    print("Параметры спектра NRZ (C = 100 Мбит/с)")
    print("По формулам: f_в = C/2, f_н = C/(2n), n — макс. серия одинаковых бит")
    print("="*60)
    print(f"Макс. серия одинаковых бит: n = {n}")
    print(f"Верхняя граница частот:     f_в = C/2 = {f_v} МГц  (чередование 1010)")
    print(f"Нижняя граница частот:     f_н = C/(2n) = C/{2*n} = {f_n:.2f} МГц  (период 2n тактов)")
    print(f"Середина спектра:           f_1/2 = (f_в+f_н)/2 = {f_half:.2f} МГц")
    print(f"Средняя частота:            f_ср = (10·f_в/2 + 3·f_в/3 + 5·f_в/5 + 6·f_в/6)/24 = {f_sr:.2f} МГц")
    print(f"Ширина спектра:             S = f_в - f_н = {S:.2f} МГц")
    print(f"Полоса пропускания:         от 0 Гц (DC) до ≈ {f_v} МГц")
    print("\n--- Что за что отвечает ---")
    print("f_в = C/2 — теоретический максимум при чередовании 1 и 0 (период = 2 такта).")
    print("f_н = C/(2n) — определяется самой длинной серией одинаковых бит (n тактов подряд → период 2n).")
    print("S = f_в - f_н — ширина спектра. Полоса пропускания — от 0 до ≈ f_в (есть DC).")

if __name__ == "__main__":
    main()
