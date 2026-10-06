"""Builds the chart-library spike: slide 04 with its stacked area chart drawn three other ways.

Writes docs/spikes/001-chart-library/04-{echarts,chartjs,svg}.html from the archetype, replacing
only the chart's library and script. Same data, same geometry rules as the Highcharts original:
plot top 10 px, bottom band 50 px, points at category centres, bands stacked Poor at the bottom to
Excellent on top at 0.95 opacity, legend Excellent first as 16 x 4 strips, the position marker at
category 3.5 inside the Average band with its two-line label box.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'spikes' / '001-chart-library'
SOURCE = (ROOT / 'archetypes' / '04-Slide-Cybersecurity-Maturity.html').read_text(encoding='utf-8')

DATA = """    const chartData = {
        categories: ['Startups', 'Small Biz', 'Mid-Market', 'Enterprise', 'Large Ent.', 'Fortune 500'],
        series: {
            poor: [20, 15, 8, 5, 2, 0],
            belowAverage: [35, 30, 22, 15, 8, 3],
            average: [30, 35, 35, 30, 25, 15],
            good: [12, 15, 25, 35, 40, 42],
            excellent: [3, 5, 10, 15, 25, 40]
        }
    };
    // Bottom to top.
    const bands = [
        ['Poor', chartData.series.poor, '#8B5CF6'],
        ['Below Avg', chartData.series.belowAverage, '#EF4444'],
        ['Average', chartData.series.average, '#F59E0B'],
        ['Good', chartData.series.good, '#10B981'],
        ['Excellent', chartData.series.excellent, '#3B82F6']
    ];
    // The position marker: between Enterprise and Large Ent., 16 points into the Average band.
    const marker = { category: 3.5, value: chartData.series.poor[3] + chartData.series.belowAverage[3] + 16,
                     title: 'Global Finance Corp', subtitle: 'Maturity Score' };
"""

SVG = DATA + """
    // Drawn as inline SVG: no chart library.
    document.fonts.ready.then(function () {
        const el = document.getElementById('chart-04');
        const W = el.clientWidth, H = el.clientHeight, n = chartData.categories.length;
        const top = 10, plotH = H - top - 50;
        const x = i => (i + 0.5) * W / n;
        const y = v => top + plotH * (1 - v / 100);
        const NS = 'http://www.w3.org/2000/svg';
        const add = (tag, attrs, parent) => {
            const node = document.createElementNS(NS, tag);
            for (const key in attrs) node.setAttribute(key, attrs[key]);
            parent.appendChild(node);
            return node;
        };
        const svg = add('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`,
                                 style: 'display: block; font-family: Montserrat, sans-serif' }, el);

        let base = chartData.categories.map(() => 0);
        bands.forEach(([, values, color]) => {
            const tops = values.map((v, i) => base[i] + v);
            const points = tops.map((t, i) => `${x(i)},${y(t)}`)
                .concat(base.map((b, i) => `${x(i)},${y(b)}`).reverse());
            add('polygon', { points: points.join(' '), fill: color, 'fill-opacity': 0.95 }, svg);
            base = tops;
        });

        chartData.categories.forEach((label, i) => {
            add('text', { x: x(i), y: top + plotH + 25, 'text-anchor': 'middle', fill: '#64748B',
                          'font-size': 9, 'font-weight': 600 }, svg).textContent = label;
        });

        const legend = add('g', {}, svg);
        let cursor = 0;
        bands.slice().reverse().forEach(([name, , color]) => {
            add('rect', { x: cursor, y: H - 14, width: 16, height: 4, fill: color, 'fill-opacity': 0.95 }, legend);
            const text = add('text', { x: cursor + 21, y: H - 10, fill: '#475569', 'font-size': 9.5,
                                       'font-weight': 600 }, legend);
            text.textContent = name;
            cursor += 21 + text.getComputedTextLength() + 12;
        });
        legend.setAttribute('transform', `translate(${Math.round((W - (cursor - 12)) / 2)}, 0)`);

        const mx = (marker.category + 0.5) * W / n, my = y(marker.value);
        add('circle', { cx: mx - 5, cy: my - 5, r: 5, fill: '#0A2540', stroke: '#FFFFFF', 'stroke-width': 2 }, svg);
        const box = add('g', { transform: `translate(${Math.round(mx + 6)}, ${Math.round(my - 16)})` }, svg);
        const rect = add('rect', { x: 0.5, y: 0.5, height: 33, rx: 4, fill: 'rgba(255, 255, 255, 0.95)',
                                   stroke: '#E2E8F0', 'stroke-width': 1 }, box);
        const label = add('text', { x: 5, y: 15, fill: '#0A2540', 'font-size': 9 }, box);
        add('tspan', { 'font-weight': 'bold' }, label).textContent = marker.title;
        add('tspan', { x: 5, dy: 12 }, label).textContent = marker.subtitle;
        rect.setAttribute('width', Math.ceil(label.getBBox().width) + 10);
    });
"""

ECHARTS = DATA + """
    // Apache ECharts with its SVG renderer.
    document.fonts.ready.then(function () {
        const el = document.getElementById('chart-04');
        const chart = echarts.init(el, null, { renderer: 'svg' });
        const W = el.clientWidth, H = el.clientHeight, n = chartData.categories.length;
        const top = 10, plotH = H - top - 50;
        const mx = (marker.category + 0.5) * W / n, my = top + plotH * (1 - marker.value / 100);
        chart.setOption({
            animation: false,
            textStyle: { fontFamily: 'Montserrat, sans-serif' },
            grid: { left: 0, right: 0, top: top, bottom: 50 },
            xAxis: { type: 'category', data: chartData.categories, boundaryGap: true,
                     axisLine: { show: false }, axisTick: { show: false },
                     axisLabel: { color: '#64748B', fontSize: 9, fontWeight: 600, margin: 17, interval: 0 } },
            yAxis: { type: 'value', min: 0, max: 100, show: false },
            legend: { bottom: 3, icon: 'rect', itemWidth: 16, itemHeight: 4, itemGap: 12,
                      data: bands.map(b => b[0]).reverse(),
                      textStyle: { color: '#475569', fontSize: 9.5, fontWeight: 600, padding: [0, 0, 0, 0] } },
            series: bands.map(([name, data, color]) => ({
                name, type: 'line', stack: 'maturity', data, symbol: 'none', silent: true,
                lineStyle: { width: 0 }, itemStyle: { color }, areaStyle: { color, opacity: 0.95 } })),
            graphic: [
                { type: 'circle', shape: { cx: mx - 5, cy: my - 5, r: 5 }, z: 100,
                  style: { fill: '#0A2540', stroke: '#FFFFFF', lineWidth: 2 } },
                { type: 'group', x: Math.round(mx + 6), y: Math.round(my - 16), z: 100, children: [
                    { type: 'rect', z: 100, shape: { x: 0.5, y: 0.5, width: 105, height: 33, r: 4 },
                      style: { fill: 'rgba(255, 255, 255, 0.95)', stroke: '#E2E8F0', lineWidth: 1 } },
                    { type: 'text', z: 101, x: 5, y: 7, style: { text: marker.title, fill: '#0A2540', fontSize: 9,
                      fontWeight: 'bold', fontFamily: 'Montserrat, sans-serif' } },
                    { type: 'text', z: 101, x: 5, y: 19, style: { text: marker.subtitle, fill: '#0A2540', fontSize: 9,
                      fontFamily: 'Montserrat, sans-serif' } } ] }
            ]
        });
    });
"""

CHARTJS = DATA + """
    // Chart.js (canvas), as slide 09's radar.
    document.fonts.ready.then(function () {
        const el = document.getElementById('chart-04');
        const canvas = document.createElement('canvas');
        el.appendChild(canvas);
        const font = (size, weight) => ({ family: 'Montserrat, sans-serif', size, weight });
        const alpha = hex => hex + 'F2'; // 0.95
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: chartData.categories,
                datasets: bands.map(([label, data, color], i) => ({
                    label, data, backgroundColor: alpha(color), borderWidth: 0, pointRadius: 0,
                    fill: i === 0 ? 'origin' : '-1', tension: 0 }))
            },
            options: {
                animation: false, responsive: true, maintainAspectRatio: false,
                layout: { padding: { top: 10, left: 0, right: 0, bottom: 0 } },
                events: [],
                scales: {
                    x: { offset: true, grid: { display: false }, border: { display: false },
                         ticks: { color: '#64748B', font: font(9, 600), padding: 1 } },
                    y: { stacked: true, min: 0, max: 100, display: false }
                },
                plugins: {
                    tooltip: { enabled: false },
                    legend: { position: 'bottom', reverse: true,
                              labels: { boxWidth: 16, boxHeight: 4, padding: 7, color: '#475569', font: font(9.5, 600) } }
                }
            },
            plugins: [{
                id: 'positionMarker',
                afterDatasetsDraw(chart) {
                    const { ctx, scales } = chart;
                    const step = scales.x.getPixelForValue(1) - scales.x.getPixelForValue(0);
                    const mx = scales.x.getPixelForValue(3) + step / 2, my = scales.y.getPixelForValue(marker.value);
                    ctx.save();
                    ctx.beginPath(); ctx.arc(mx - 5, my - 5, 5, 0, Math.PI * 2);
                    ctx.fillStyle = '#0A2540'; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = '#FFFFFF'; ctx.stroke();
                    const bx = Math.round(mx + 6), by = Math.round(my - 16);
                    ctx.font = 'bold 9px Montserrat, sans-serif';
                    const width = Math.ceil(Math.max(ctx.measureText(marker.title).width,
                        (ctx.font = '9px Montserrat, sans-serif', ctx.measureText(marker.subtitle).width))) + 10;
                    ctx.beginPath(); ctx.roundRect(bx + 0.5, by + 0.5, width, 33, 4);
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'; ctx.fill();
                    ctx.lineWidth = 1; ctx.strokeStyle = '#E2E8F0'; ctx.stroke();
                    ctx.fillStyle = '#0A2540';
                    ctx.font = 'bold 9px Montserrat, sans-serif'; ctx.fillText(marker.title, bx + 5, by + 15);
                    ctx.font = '9px Montserrat, sans-serif'; ctx.fillText(marker.subtitle, bx + 5, by + 27);
                    ctx.restore();
                }
            }]
        });
    });
"""

CANDIDATES = {
    'echarts': ('<script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"></script>', ECHARTS),
    'chartjs': ('<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>', CHARTJS),
    'svg': ('', SVG),
}

libraries = re.compile(r'(?:\s*<script src="https://cdn\.jsdelivr\.net/npm/highcharts@[^"]+"></script>)+')
chart_script = re.compile(r'<!-- Highcharts Implementation Script -->\s*<script>.*?</script>', re.S)
assert libraries.search(SOURCE) and chart_script.search(SOURCE)
OUT.mkdir(parents=True, exist_ok=True)
for name, (tag, script) in CANDIDATES.items():
    page = libraries.sub(('\n    ' + tag) if tag else '', SOURCE, count=1)
    page = chart_script.sub(lambda m: f'<!-- Chart: {name} candidate (spike 001) -->\n<script>\n{script}</script>', page, count=1)
    (OUT / f'04-{name}.html').write_text(page, encoding='utf-8')
    print('wrote', OUT / f'04-{name}.html')
