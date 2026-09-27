import re

with open('archetypes/04-Slide-Cybersecurity-Maturity.html', 'r') as f:
    content = f.read()

# Change reversed: false to reversed: true
content = content.replace('reversed: false', 'reversed: true')

# Replace the series block
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

# Notice we also have to fix the position marker calculating the Y position
# Currently it uses:
# const poorHeight = chartData.series.poor[fsrIndex];
# const belowAvgHeight = chartData.series.belowAverage[fsrIndex];
# const belowAvgTop = poorHeight + belowAvgHeight;
# const fsrPosition = belowAvgTop + 16;
#
# If the stack goes: Poor on bottom, Below Avg, Average, Good, Excellent.
# Then Poor is at the bottom (y=0 to y=PoorHeight).
# Below Avg is (y=PoorHeight to y=PoorHeight+BelowAvgHeight).
# So belowAvgTop is correct for the top of Below Avg, and fsrPosition goes into the Average band.
# This logic doesn't need to change if Poor is still visually at the bottom.
# Let's write the file.

with open('archetypes/04-Slide-Cybersecurity-Maturity.html', 'w') as f:
    f.write(content)
