import re

with open('archetypes/04-Slide-Cybersecurity-Maturity.html', 'r') as f:
    content = f.read()

old_series = """series: [{
            name: 'Poor',
            data: chartData.series.poor,
            color: '#8B5CF6' 
        }, {
            name: 'Below Avg',
            data: chartData.series.belowAverage,
            color: '#EF4444' 
        }, {
            name: 'Average',
            data: chartData.series.average,
            color: '#F59E0B' 
        }, {
            name: 'Good',
            data: chartData.series.good,
            color: '#10B981' 
        }, {
            name: 'Excellent',
            data: chartData.series.excellent,
            color: '#3B82F6' 
        }],"""

# The goal:
# Bottom layer: Poor (Purple)
# Next layer: Below Avg (Red)
# Next layer: Average (Orange)
# Next layer: Good (Green)
# Top layer: Excellent (Blue)
# Highcharts draws the LAST item in the series array at the TOP.
# So to have Excellent at the top and Poor at the bottom, 
# Poor should be FIRST in the array, and Excellent should be LAST.
# BUT Highcharts also lets you use `reversed: true` on the yAxis or in the legend.
# Wait, let me check the data.
# The user says "Poor is still at the top, it should start with poor increasing the band".
# Let's look at the arrays:
# poor: [20, 15, 8, 5, 2, 0],
# excellent: [3, 5, 10, 15, 25, 40]
# We want poor to increase left to right? No, image 5 shows Purple starting moderate on the left, but tapering to NOTHING on the right. That matches `poor: [20, 15, 8, 5, 2, 0]`.
# Excellent (Blue) starts as nothing on the left `3`, and increases to `40` on the right.
# In image 5, Blue is at the TOP. Purple is at the BOTTOM.
# Highcharts draws the FIRST series at the BOTTOM.
# So: 1. Poor (Purple), 2. Below Avg, 3. Average, 4. Good, 5. Excellent.
# This is EXACTLY what I wrote above. Why did the user say it's reversed?
# Because Highcharts might be stacking it differently.
# Let's look at image 4. In image 4, Blue is at the bottom. Blue is Excellent.
# This means Excellent is currently rendering at the bottom!
# Why? Because in my LAST commit, Excellent was at the bottom (I put Poor first, but maybe Highcharts renders first at top?)
# Let's explicitly put Excellent FIRST in the array (so it renders at the bottom? Or top?)
# If Image 4 shows Blue at the bottom, and my last commit had Poor first... that means the FIRST item in the array renders at the BOTTOM. 
# Wait, my last commit put Poor first, and the user said "Poor is still at the top". That means the FIRST item renders at the BOTTOM, so if Poor was first, it was at the bottom... wait, if Poor was first, it rendered at the bottom in the code but... wait.
# Let's just reverse the array explicitly to be Excellent, Good, Average, Below Avg, Poor.

new_series = """series: [{
            name: 'Excellent',
            data: chartData.series.excellent,
            color: '#3B82F6' 
        }, {
            name: 'Good',
            data: chartData.series.good,
            color: '#10B981' 
        }, {
            name: 'Average',
            data: chartData.series.average,
            color: '#F59E0B' 
        }, {
            name: 'Below Avg',
            data: chartData.series.belowAverage,
            color: '#EF4444' 
        }, {
            name: 'Poor',
            data: chartData.series.poor,
            color: '#8B5CF6' 
        }],"""

content = content.replace(old_series, new_series)

with open('archetypes/04-Slide-Cybersecurity-Maturity.html', 'w') as f:
    f.write(content)
