def scrape_folder(path,save=False):
    import os
    import tinytag as tt
    import pandas as pd
    import string
    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts = [ts]
    tag=[]
    printable = set(string.printable)

    for root, dirs, files in os.walk(path+'/Music'):
        for f in files:
            if os.path.splitext(f)[1] == '.mp3':
                fullpath = os.path.join(root, f)
                tag.append(tt.TinyTag.get(fullpath))
    # INDEXES SUPPORTED BY TINYTAG
    index=["album","albumartist","artist","audio_offset","bitrate","channels","comment","composer","disc","disc_total","duration","extra","filesize","genre","samplerate","title","track","track_total","year"]
    info=[]
    for j in range(0,len(tag)):
        info.append([])
        for i in range(0,len(index)):
            s=getattr(tag[j],index[i]) if getattr(tag[j],index[i]) is not None else ''
            s=''.join(filter(lambda x: x in printable, s)).replace('\n','').replace('\r','') if isinstance(s,str) else s
            info[j].append(s)

    df = pd.DataFrame(info,columns=index)

    tsl=ts*(len(tag))
    df.insert(loc=0,column='Timestamp',value=tsl)
    if save:
        df.to_csv(path+'/scraped_data.csv')

    print('Scrape processed')
    return df