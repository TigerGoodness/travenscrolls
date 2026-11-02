from instance.database import *
import re
###TEKSTI FAILID###
##LOEB RIDU##
def fail_open_read_lines(direction):
    fail=open(direction, 'r', encoding='UTF-8')
    file=fail.readlines()
    file = striping(file)
    fail.close()
    return file
##LOEB##
def fail_open_read(direction):
    fail=open(direction, 'r', encoding='UTF-8')
    file=fail.read()
    fail.close()
    return file
##PUHASTAB##
def striping(input):
    output=[]
    for i in input:
        a=i.strip()
        output+=[a]
    return output
##LÕIKAB \n\n##
def cutter(fail):
    fail=fail.split('\n\n')
    return fail
##LÕIKAB \n##
def cutter2(fail):
    fail=fail.split('\n')
    return fail
##LÕIKAB##
def cutter3(fail1, fail2, fail3):
    a=len(fail1)+len(fail2)+len(fail3)
    return a
##FAILI LISAB##
def fail_append(direction, input):
    file = open(direction, 'a', encoding='UTF-8')
    file.write(input)
    file.close()
##FAILI KIRJUTAB##
def fail_write(direction, input):
    file = open(direction, 'w', encoding='UTF-8')
    file.write(f'\n{input}')
    file.close()
##LOEB JA TEEB SÕNASTIKU##
def read_and_dictionary(direction):
    file=open(direction, 'r', encoding='UTF-8')
    a=file.readlines()
    dic={}
    file.close()
    while True:
        if a==[]:
            break
        dic[a[0].strip()]=a[1].strip()
        del a[:3]
    return dic
def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        session.execute(table.delete())
    return
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
def lisa(klassid, taustad, rassid, loitsud, vaike_tekst):
    for klass in klassid:
        file = fail_open_read(f'muu/Class_txt/{klass}.txt')
        file=cutter(file)
        klasslist = []
        for i in file:
            i = cutter2(i)
            klasslist.append(i)
        if klass not in ['Artificer']:
            try:
                db.session.add(
                    Klass(nimi=klasslist[0][0],
                          saving_throw=klasslist[2][4].split(': ')[1],
                          text=klasslist[0][1],
                          hit_points=klasslist[1][1].split(' ')[2],
                          proficiencies='\n'.join(klasslist[2][1:]),
                          equipment='\n'.join(klasslist[3][1:]),
                          features=klasslist[5][0],
                          lvl1='\t'.join(klasslist[4][0].split('.')[1:]),
                          lvl2='\t'.join(klasslist[4][1].split('.')[1:]),
                          lvl3='\t'.join(klasslist[4][2].split('.')[1:]),
                          lvl4='\t'.join(klasslist[4][3].split('.')[1:]),
                          lvl5='\t'.join(klasslist[4][4].split('.')[1:]),
                          lvl6='\t'.join(klasslist[4][5].split('.')[1:]),
                          lvl7='\t'.join(klasslist[4][6].split('.')[1:]),
                          lvl8='\t'.join(klasslist[4][7].split('.')[1:]),
                          lvl9='\t'.join(klasslist[4][8].split('.')[1:]),
                          lvl10='\t'.join(klasslist[4][9].split('.')[1:]),
                          lvl11='\t'.join(klasslist[4][10].split('.')[1:]),
                          lvl12='\t'.join(klasslist[4][11].split('.')[1:]),
                          lvl13='\t'.join(klasslist[4][12].split('.')[1:]),
                          lvl14='\t'.join(klasslist[4][13].split('.')[1:]),
                          lvl15='\t'.join(klasslist[4][14].split('.')[1:]),
                          lvl16='\t'.join(klasslist[4][15].split('.')[1:]),
                          lvl17='\t'.join(klasslist[4][16].split('.')[1:]),
                          lvl18='\t'.join(klasslist[4][17].split('.')[1:]),
                          lvl19='\t'.join(klasslist[4][18].split('.')[1:]),
                          lvl20='\t'.join(klasslist[4][19].split('.')[1:]),
                          small_text=f'{vaike_tekst[klass]}')
                )
            except:
                db.session.add(
                    Klass(nimi=klasslist[0][0],
                      saving_throw=klasslist[1][0],
                      text=klasslist[0][1],
                      small_text=f'{vaike_tekst[klass]}')
            )

    for taust in taustad:
        db.session.add(
            Taust(nimi=taust,
                  skill_proficiencies='\n'.join(fail_open_read_lines(f'muu/BG_choosing/{taust}.txt')),
                  text='\n\n'.join(cutter(fail_open_read(f'muu/BG_txt/{taust}.txt'))))
        )

    for rass in rassid:
        db.session.add(
            Rass(nimi=rass,
                  ability_score_increase='\n'.join(fail_open_read_lines(f'muu/Race_choosing/{rass}.txt')),
                  text='\n\n'.join(cutter(fail_open_read(f'muu/Race_txt/{rass}.txt'))))
        )

    fail = fail_open_read(f'muu/Spells.txt')
    fail = cutter(fail)
    spells = []
    for i in fail:
        i = cutter2(i)
        spells.append(i)
    for loits in loitsud:
        for spell in spells:
            if loits in spell:
                db.session.add(
                    Loits(nimi = spell[0],
                          level = spell[1].split(' - ')[0][6:],
                          kool = spell[1].split(' - ')[1],
                          aeg = spell[2].split(': ')[1],
                          kaugus = spell[3].split(': ')[1],
                          koostisosad = spell[4].split(': ')[1],
                          kestvus = spell[5].split(': ')[1],
                          text = '\n'.join(spell[6:],))
                )

    fail=fail_open_read(f'muu/Features.txt')
    fail=cutter(fail)
    for i in fail:
        i=cutter2(i)
        db.session.add(
            Features(nimi=i[0],
                     text=i[1])
        )