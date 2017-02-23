import requests
starts = [0, 0, 0, 0, 0, 0, 40, 0, 88, 63, 36]
tot = 0
tot_l = 0
latest = [0, 1, 2, 3, 4]
ub = [0]
i = 0
print '\nIndividual download counts:'
for release in requests.get('https://api.github.com/repos/lars-frogner/astrophotography-lab/releases').json():
    for release_assets in release['assets']:
    
        d = release_assets['download_count'] + starts[i]
        
        tot += d
        if i in latest: tot_l += d
        name = release_assets['name'].split('-win-') if not i in ub else release_assets['name'].split('-ubuntu-')
        
        print '%s: %d' % (name[0].replace('-', ' ') + (' Windows ' if not i in ub else ' Ubuntu ') + name[1].split('.')[0], d)
        i += 1
      
print '\nDownloads of latest: %s' % tot_l
print 'Total downloads: %d' % tot