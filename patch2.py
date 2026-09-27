import re

with open('archetypes/04-Slide-Cybersecurity-Maturity.html', 'r') as f:
    content = f.read()

# Change reversed back to false
content = content.replace('reversed: true', 'reversed: false')

# Put the series in the exact order requested: Poor at the bottom (first in array), Excellent at the top (last in array).
old_series = """series: [{
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

new_series = """series: [{
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

if old_series in content:
    content = content.replace(old_series, new_series)
else:
    print("Could not find old series block")

with open('archetypes/04-Slide-Cybersecurity-Maturity.html', 'w') as f:
    f.write(content)
