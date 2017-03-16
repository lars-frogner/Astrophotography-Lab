import requests
starts = [0, 0, 0, 0, 0, 0, 0, 0, 40, 0, 88, 63, 36]
tot = 0
tot_l = 0
latest = [0, 1]
i = 0
print '\nIndividual download counts:'
for release in requests.get('https://api.github.com/repos/lars-frogner/astrophotography-lab/releases').json():


    for release_assets in release['assets']:
    
        d = release_assets['download_count'] + starts[i]
        
        tot += d
        if i in latest: tot_l += d

        print '%-34s %d' % (release_assets['name'].replace('.zip', '').replace('.tar.gz', ''), d)
        
        i += 1
      
print '\nDownloads of latest version: %s' % tot_l
print 'Total downloads: %d' % tot