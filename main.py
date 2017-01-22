import requests
import matplotlib.pyplot as plt
import iso8601
import os
import numpy

def req2json(url):
    return requests.get(url, auth=('ou\pi-api-public', 'M53$dx7,d3fP8')).json()

def display(buildingNum, interval, startTime):
    try:
        building=buildings[buildingNum]
        webid = mapping[building]
        if 'mo' in startTime:
            denom = 86400*30
            unit = 'Month'
        elif 'w' in startTime:
            denom = 86400*7
            unit = 'Week'
        elif 'd' in startTime:
            denom = 86400
            unit = 'Day'
        elif 'h' in startTime:
            denom = 3600
            unit = 'Hour'
        elif 'm' in startTime:
            denom = 60
            unit = 'Minute'

        j = req2json('https://bldg-pi-api.ou.ad3.ucdavis.edu/piwebapi/elements/' + webid + '/elements')
        nextURL = j['Items'][0]['Links']['InterpolatedData']+'?namefilter=Demand_kBtu&interval='+interval+'&startTime=-'+startTime
        j = req2json(nextURL)
    except:
        print('Error: URL: ' + building)
        print('URL:\n' + nextURL)
        input('')
        return

    try:
        timestamps = []
        elec = []
        for e in j['Items'][0]['Items']:
            if 'Good' in e and e['Good'] == False:
                print('ERROR: DEVICE FAILED!!', iso8601.parse_date(e['Timestamp']))
                print(e['Value'])
            else:
                elec.append(e['Value'])
                timestamps.append(int(iso8601.parse_date(e['Timestamp']).timestamp()))
    except:
        print('Error: JSON structure: ' + building)
        print('URL:\n' + nextURL)
        input('')
        return

    try:
        Y = numpy.fft.fft(elec)
        L = timestamps[-1] - timestamps[0]
        Fs = timestamps[1] - timestamps[0]
        currentTime = max(timestamps)
        timestamps = [(x - currentTime)/denom for x in timestamps]
        P2  = abs(Y/L)[::-2]
        P1 = P2[:len(P2)//2+1]
        f = []
        for i in range(1,len(P1)+1):
            f.append((1/Fs) * i / (2 * len(P1)))
    except:
        print('Error: FFT')
        print('URL:\n' + nextURL)
        input('')
        return
    try:
        # Temperature
        j = req2json('https://bldg-pi-api.ou.ad3.ucdavis.edu/piwebapi/streams/A0EbgZy4oKQ9kiBiZJTW7eugwvuNJoeTC5hGUXQAVXTB8PA0hb_A-jKzkKp44rKK973OwVVRJTC1BRlxDRUZTXFVDREFWSVNcV0VBVEhFUnxPQVQ/interpolated?interval='+interval+'&startTime=-'+startTime)
        temps = []
        for t in j['Items']:
            temps.append(t['Value'])
    except:
        print('Error: JSON structure: temperature')
        print('URL:\n' + nextURL)
        input('')
        return

    try:
        # Waveform
        plt.figure(figsize=(22,11))
        plt.subplot(221)
        plt.plot(timestamps, elec)
        plt.title(building + ' Electricity Demand Trend')
        plt.xlabel('Time ('+unit+')')
        plt.ylabel('Electricity Demand (kBut)')

        # FFT
        plt.subplot(222)
        plt.title('FFT Analysis: Frequency')
        plt.plot(f, P1, 'm')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')

        plt.subplot(224)
        plt.title('FFT Analysis: Period (1/Freq)')
        plt.plot([1/x/denom for x in f], P1, 'r')
        plt.xlabel('Period ('+unit+')')
        plt.ylabel('Amplitude')
        #plt.xticks([0,10,20,30], ['a', 'b', 'c', 'd'])

        # Temperature
        plt.subplot(223)
        plt.plot(timestamps, temps, 'g')
        plt.title('Temperature')
        plt.xlabel('Time ('+unit+')')
        plt.ylabel('Temp (F)')

        plt.savefig('fig.png', bbox_inches='tight')
        plt.show()
    except:
        print('ERROR: plot: ' + building)
        plt.show()
        input('')

# Building vs WebId
j = req2json('https://bldg-pi-api.ou.ad3.ucdavis.edu/piwebapi/elements/E0bgZy4oKQ9kiBiZJTW7eugwvgV_Y00J5BGt6DwVwsURwwVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdT/elements?selectedfields=items.name;items.webid')
mapping = {}
buildings = []
for m in j['Items']:
    mapping[m['Name']] = m['WebId']
    buildings.append(m['Name'])

while True:
    print("===== List of Buildings on UCD Campus =====")
    for i, b in enumerate(buildings):
        print(i, b)
    # Electricity
    buildingNum = int(input('\nEnter building number: '))
    interval = input('Enter interval: ')
    startTime = input('Enter length: ')
    print()
    display(buildingNum, interval, startTime)

## Total
#j = req2json('https://bldg-pi-api.ou.ad3.ucdavis.edu/piwebapi/streamsets/E0bgZy4oKQ9kiBiZJTW7eugwvlfctjd_5RGrBZiQlqSuWwVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXEFDQURFTUlDIFNVUkdFIEJVSUxESU5H/recorded?nameFilter=total_demand')
#
#records = j['Items'][0]['Items']
#values = []
#timestamps = []
#for i in records:
#    #print(i['Timestamp'], i['Value'])
#    values.append(i['Value'])
#    timestamps.append(int(iso8601.parse_date(i['Timestamp']).timestamp()))

#plt.plot(timestamps, values)
#plt.show()





################
#j = req2json('https://bldg-pi-api.ou.ad3.ucdavis.edu/piwebapi/elements/E0bgZy4oKQ9kiBiZJTW7eugwvgV_Y00J5BGt6DwVwsURwwVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdT/elements')

#buildings = []
#for b in j['Items']:
    #buildings.append(b['Name'])

#print(buildings)
################


