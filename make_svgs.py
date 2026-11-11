#!/usr/bin/env python3
"""Generates the animated SVGs for the GitHub profile README (pure CSS animation)."""
import math

BG, PANEL, GRID = "#0d1117", "#161b22", "#21262d"
GREEN, CYAN, YELLOW, PINK, MUTED, WHITE = "#3fb950", "#39c5cf", "#e3b341", "#f778ba", "#8b949e", "#e6edf3"
MONO = "ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"


# ----------------------------------------------------------------- banner
def banner():
    W, H = 1000, 320
    px, py, pw, ph = 372, 46, 600, 236          # waveform panel
    lx = px + 92                                # where traces start (after signal names)
    tw = pw - 104                               # visible trace width
    P = 400                                     # repeat period of every trace (px)
    reps = 3                                    # draw 3 periods so the scroll is seamless
    rows = {"clk": 0, "rst_n": 1, "data[7:0]": 2, "valid": 3, "ready": 4, "vout": 5}
    rh = 36
    def y0(r): return py + 34 + r * rh           # top of a row

    # clock: 10 cycles per period
    clk = []
    x = 0
    for _ in range(10 * reps):
        clk += [f"{x},{14}", f"{x},{0}", f"{x+20},{0}", f"{x+20},{14}"]
        x += 40
    clk_path = "M" + " L".join(clk)

    # rst_n: low at the very start of each period, then high
    rst = []
    for k in range(reps):
        o = k * P
        rst += [f"{o},14", f"{o+30},14", f"{o+30},0", f"{o+P},0"]
    rst_path = "M" + " L".join(rst)

    # data bus: 5 values per period, drawn as hexagon segments
    vals = ["A5", "3C", "7E", "C3", "5A"]
    bus, labels = [], []
    for k in range(reps):
        for i, v in enumerate(vals):
            a = k * P + i * 80
            b = a + 80
            bus.append(f"M{a+4},0 L{b-4},0 L{b},7 L{b-4},14 L{a+4},14 L{a},7 Z")
            labels.append((a + 40, v))
    # valid / ready handshake pulses, one beat per data value
    valid, ready = [], []
    for k in range(reps):
        for i in range(5):
            a = k * P + i * 80
            valid += [f"{a+0},14", f"{a+0},0", f"{a+40},0", f"{a+40},14", f"{a+80},14"]
            ready += [f"{a+0},14", f"{a+20},14", f"{a+20},0", f"{a+60},0", f"{a+60},14", f"{a+80},14"]
    valid_path = "M" + " L".join(valid)
    ready_path = "M" + " L".join(ready)

    # analog: damped-looking sine (2 cycles per period) for vout
    pts = []
    for i in range(0, P * reps + 1, 4):
        t = i / P * 2 * math.pi * 2
        pts.append(f"{i},{14 - 14 * (0.5 + 0.45 * math.sin(t) + 0.05 * math.sin(5 * t))}")
    sine_path = "M" + " L".join(pts)

    def trace(row, d, color, fill=False):
        f = f'fill="{color}" fill-opacity="0.12"' if fill else 'fill="none"'
        return (f'<path transform="translate(0,{y0(row)})" d="{d}" stroke="{color}" '
                f'stroke-width="2" {f} stroke-linejoin="round"/>')

    bus_svg = "".join(
        f'<path transform="translate(0,{y0(2)})" d="{d}" stroke="{YELLOW}" stroke-width="2" '
        f'fill="{YELLOW}" fill-opacity="0.10"/>' for d in bus)
    bus_txt = "".join(
        f'<text x="{x}" y="{y0(2)+11}" class="mono" font-size="11" fill="{YELLOW}" '
        f'text-anchor="middle">8\'h{v}</text>' for x, v in labels)

    names = "".join(
        f'<text x="{px+14}" y="{y0(r)+11}" class="mono" font-size="12" fill="{MUTED}">{n}</text>'
        for n, r in rows.items())

    grid = "".join(
        f'<line x1="{lx+i*40}" y1="{py+26}" x2="{lx+i*40}" y2="{py+ph-10}" stroke="{GRID}" stroke-width="1"/>'
        for i in range(tw // 40 + 1))

    roles = ["RTL Design", "Design Verification", "FPGA Prototyping", "Analog &amp; PCB Design"]
    n = len(roles)
    T = 10
    role_css, role_svg = [], []
    for i, r in enumerate(roles):
        a, b = 100 * i / n, 100 * (i + 1) / n
        role_css.append(
            f"@keyframes r{i}{{0%{{opacity:0}}{a:.1f}%{{opacity:0;transform:translateY(8px)}}"
            f"{a+3:.1f}%{{opacity:1;transform:translateY(0)}}{b-3:.1f}%{{opacity:1;transform:translateY(0)}}"
            f"{b:.1f}%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}"
            f".r{i}{{animation:r{i} {T}s linear infinite;opacity:0}}")
        role_svg.append(f'<text class="r{i}" x="40" y="168" font-size="25" font-weight="600" fill="{CYAN}" '
                        f'font-family="{SANS}">{r}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Ish Bedi: RTL design, design verification, FPGA, analog and PCB design">
<style>
  .mono {{ font-family: {MONO}; }}
  @keyframes scroll {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-{P}px) }} }}
  .wave {{ animation: scroll 6s linear infinite; }}
  @keyframes sweep {{ 0% {{ transform: translateX(0) }} 100% {{ transform: translateX({tw}px) }} }}
  .cursor {{ animation: sweep 6s ease-in-out infinite alternate; }}
  @keyframes blink {{ 0%,45% {{ opacity: 1 }} 50%,95% {{ opacity: .25 }} 100% {{ opacity: 1 }} }}
  .blink {{ animation: blink 1.6s steps(1) infinite; }}
  @keyframes caret {{ 0%,49% {{ opacity: 1 }} 50%,100% {{ opacity: 0 }} }}
  .caret {{ animation: caret 1s steps(1) infinite; }}
  {"".join(role_css)}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
<!-- left: name -->
<text x="40" y="96" font-family="{SANS}" font-size="50" font-weight="700" fill="{WHITE}">Ish Bedi</text>
<text x="42" y="126" font-family="{SANS}" font-size="15" fill="{MUTED}">Electrical Engineering · McMaster</text>
{"".join(role_svg)}
<rect class="caret" x="40" y="182" width="12" height="3" fill="{CYAN}"/>
<g font-family="{MONO}" font-size="13" fill="{MUTED}">
  <text x="40" y="226">// SystemVerilog · Verilog · RISC-V</text>
  <text x="40" y="248">// Testbenches · FPGA · Altium</text>
</g>
<g class="blink"><rect x="40" y="264" width="150" height="26" rx="6" fill="{GREEN}" fill-opacity="0.15" stroke="{GREEN}"/>
<text x="115" y="282" text-anchor="middle" class="mono" font-size="13" font-weight="700" fill="{GREEN}">● ALL TESTS PASS</text></g>
<!-- right: waveform viewer -->
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="{PANEL}" stroke="{GRID}"/>
<circle cx="{px+16}" cy="{py+14}" r="4.5" fill="#f85149"/><circle cx="{px+30}" cy="{py+14}" r="4.5" fill="{YELLOW}"/><circle cx="{px+44}" cy="{py+14}" r="4.5" fill="{GREEN}"/>
<text x="{px+pw-14}" y="{py+18}" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">tb_soc.vcd — 100 MHz</text>
{names}
<clipPath id="clip"><rect x="{lx}" y="{py+26}" width="{tw}" height="{ph-30}"/></clipPath>
<g clip-path="url(#clip)">
  {grid}
  <g transform="translate({lx},0)"><g class="wave">
    {trace(0, clk_path, GREEN)}
    {trace(1, rst_path, PINK)}
    {bus_svg}{bus_txt}
    {trace(3, valid_path, CYAN)}
    {trace(4, ready_path, CYAN)}
    {trace(5, sine_path, "#a371f7")}
  </g></g>
  <g class="cursor" transform="translate({lx},0)"><line x1="0" y1="{py+28}" x2="0" y2="{py+ph-8}" stroke="{WHITE}" stroke-opacity="0.55" stroke-dasharray="4 3"/></g>
</g>
</svg>'''
    open("assets/banner.svg", "w").write(svg)


# ----------------------------------------------------------------- testbench terminal
def terminal():
    lines = [
        ("$ make test", WHITE, False),
        ("[tb_alu]      20,640 vectors vs reference model ......", MUTED, True),
        ("[tb_imm_gen]  I / S / B / U / J immediate formats ....", MUTED, True),
        ("[tb_fifo]     reset · full · empty · push+pop priority", MUTED, True),
        ("[tb_cycles]   R-type = 4 cycles · load = 5 cycles ....", MUTED, True),
        ("[tb_uart]     1,159 TX edges on exact bit boundaries .", MUTED, True),
        ("[tb_soc]      fib(40) over UART -> \"102334155\" .......", MUTED, True),
        ("✓ all testbenches passed", GREEN, False),
    ]
    W, H = 1000, 60 + 26 * len(lines)
    T = 14.0
    css, body = [], []
    for i, (txt, color, ok) in enumerate(lines):
        start = 4 + i * 9          # % of the loop when the line appears
        css.append(f"@keyframes l{i}{{0%,{start}%{{opacity:0}}{start+2}%,92%{{opacity:1}}97%,100%{{opacity:0}}}}"
                   f".l{i}{{animation:l{i} {T}s linear infinite;opacity:0}}")
        y = 52 + i * 26
        body.append(f'<g class="l{i}"><text x="28" y="{y}" fill="{color}">{txt}</text>'
                    + (f'<text x="{W-34}" y="{y}" text-anchor="end" fill="{GREEN}" font-weight="700">PASS</text>' if ok else "")
                    + "</g>")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Testbench results: all tests pass">
<style>
  text {{ font-family: {MONO}; font-size: 15px; white-space: pre; }}
  {"".join(css)}
</style>
<rect width="{W}" height="{H}" rx="12" fill="{PANEL}" stroke="{GRID}"/>
<circle cx="20" cy="18" r="5" fill="#f85149"/><circle cx="36" cy="18" r="5" fill="{YELLOW}"/><circle cx="52" cy="18" r="5" fill="{GREEN}"/>
<text x="{W/2}" y="22" text-anchor="middle" fill="{MUTED}" style="font-size:12px">verification — icarus verilog</text>
{"".join(body)}
</svg>'''
    open("assets/testbench.svg", "w").write(svg)


if __name__ == "__main__":
    import os
    os.makedirs("assets", exist_ok=True)
    banner()
    terminal()
    print("wrote assets/banner.svg, assets/testbench.svg")
