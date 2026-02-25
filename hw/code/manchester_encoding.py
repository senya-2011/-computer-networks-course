# -*- coding: utf-8 -*-
"""
Манчестерское кодирование строки "ААД" (hex: C0 C0 C4).
Визуализация уровня сигнала и проверка формул для спектра M2.
"""

import matplotlib
matplotlib.use('Agg')  # чтобы сохранять в файл без дисплея
import matplotlib.pyplot as plt
import numpy as np

# Исходное сообщение: "ААД" в hex = C0 C0 C4
HEX_BYTES = [0xC0, 0xC0, 0xC4]  # C0, C0, C4

def bytes_to_bits_msb_first(bytes_list):
    """Преобразование байтов в список бит (старший бит первым)."""
    bits = []
    for b in bytes_list:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def manchester_encode(bits):
    """
    Манчестерский код: в середине каждого битового такта всегда есть переход
    (по нему приёмник синхронизируется). Вариант: 0 = низкий→высокий, 1 = высокий→низкий.
    (Этот же вариант используют в Ethernet — стандарт IEEE 802.3; бывает и обратное назначение.)
    """
    signal_t = []
    signal_v = []
    t = 0.0
    T_bit = 1.0  # длительность одного бита (нормированная)
    T_half = T_bit / 2
    for bit in bits:
        if bit == 0:
            # 0: низкий → высокий
            signal_t.extend([t, t + T_half - 1e-9, t + T_half])
            signal_v.extend([-1, -1, 1])
            signal_t.append(t + T_bit)
            signal_v.append(1)
        else:
            # 1: высокий → низкий
            signal_t.extend([t, t + T_half - 1e-9, t + T_half])
            signal_v.extend([1, 1, -1])
            signal_t.append(t + T_bit)
            signal_v.append(-1)
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

    t, v = manchester_encode(bits)

    fig, ax = plt.subplots(figsize=(14, 3))
    ax.step(t, v, where='post', color='#1f77b4', linewidth=1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([-1, 1])
    ax.set_yticklabels(['Низкий', 'Высокий'])
    ax.set_xlabel('Время (нормированные единицы, 1 ед. = 1 бит)')
    ax.set_ylabel('Уровень сигнала')
    ax.set_title('Манчестерское кодирование: "ААД" (C0 C0 C4)')
    # Ось времени: метки через каждые 4 (0, 4, 8, 12, 16, 20, 24)
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ax.set_xticklabels(['0', '4', '8', '12', '16', '20', '24'])
    ax.grid(True, axis='x', alpha=0.5)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5)

    # Пунктирные линии между битами — границы тактов
    for x in range(1, n_bits):
        ax.axvline(x, color='gray', linestyle='--', linewidth=0.7, alpha=0.8)

    # Подписи бит по центру каждого такта
    for i in range(n_bits):
        ax.annotate(str(bits[i]), xy=(i + 0.5, 1.3), ha='center', fontsize=9)

    # # Пояснение: как читать манчестер
    # rule = (
    #     "Как читать: один бит = один такт (одна ячейка по времени).\n"
    #     "В середине каждого такта всегда есть переход:\n"
    #     "  • бит 0 → переход вверх (низ → верх)\n"
    #     "  • бит 1 → переход вниз (верх → низ)"
    # )
    # ax.text(0.99, 0.02, rule, transform=ax.transAxes, fontsize=8,
    #         verticalalignment='bottom', horizontalalignment='right',
    #         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    plt.savefig('d:/itmo/seti/manchester_signal.png', dpi=150, bbox_inches='tight')
    print("\nГрафик сохранён: manchester_signal.png")

    # --- Спектр M2 (Манчестер): по правильным формулам ---
    # В каждом такте есть переход в середине → нет DC, нижняя граница C/2; верхняя C.
    C_MHz = 100
    f_v = C_MHz
    f_n = C_MHz / 2
    f_half = (f_v + f_n) / 2
    f_sr = (30 * f_v + 18 * f_n) / 48
    S = f_v - f_n
    F = f_v - f_n

    print("\n" + "="*60)
    print("Параметры спектра M2 — Манчестер (C = 100 Мбит/с)")
    print("По формулам: f_в = C, f_н = C/2 (нет DC), S = F = C/2")
    print("="*60)
    print(f"Верхняя граница частот:     f_в = C = {f_v} МГц")
    print(f"Нижняя граница частот:     f_н = C/2 = {f_n} МГц  (манчестер без постоянной составляющей)")
    print(f"Середина спектра:           f_1/2 = (f_в+f_н)/2 = {f_half} МГц")
    print(f"Средняя частота:            f_ср = (30*f_в + 18*f_н)/48 = {f_sr} МГц")
    print(f"Ширина спектра:             S = f_в - f_н = {S} МГц")
    print(f"Полоса пропускания:         F = f_в - f_н = {F} МГц  (от f_н до f_в)")
    print("\n--- Что за что отвечает ---")
    print("f_в = C — верхняя граница (переход в середине каждого такта даёт макс. частоту).")
    print("f_н = C/2 — нет DC, спектр начинается с C/2. Не зависит от сообщения.")
    print("S = F = C/2 — ширина спектра и полоса пропускания.")

if __name__ == "__main__":
    main()
