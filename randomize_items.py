import random
import struct
import json

def signed_byte(b):
    return b - 256 if b >= 128 else b

with open('data/data.json') as json_file:
    DATA = json.loads(json_file.read())

MAGIC = DATA['Magic']

def get_stats(tbl):

    with open('tbl\stella_item_list.tbl', 'rb') as tbl_file:
        tbl_data = tbl_file.read()

    file_name = tbl[4:-4]

    if list(tbl_data)[ : 102] != MAGIC or tbl_data[106] != 4 or tbl_data[-1] != 11:
        print('Error: invalid magic')
        return 0

    #Size
    size = int.from_bytes(tbl_data[102 : 106], byteorder = 'little')
    table_name_size = tbl_data[107]
    table_name = tbl_data[108 : 108 + table_name_size].decode('utf-8')
    
    #Indexes check
    for _ in range(size + 1):
        if int.from_bytes(tbl_data[108 + table_name_size + 5 * _ : 112 + table_name_size + 5 * _], byteorder = 'little') != _ + 2:
            print('Error: index check failed')
            return 0

    #Param table
    new_offset = 112 + table_name_size + size * 5
    
    if list(tbl_data[new_offset : new_offset + 5]) != [5, 3, 0, 0, 0] or tbl_data[new_offset + 5] != table_name_size or tbl_data[new_offset + 6 : new_offset + 6 + tbl_data[new_offset + 5]].decode('utf-8') != table_name:
        print('Error: param table header check failed')
        return 0

    new_offset += 6 + tbl_data[new_offset + 5]
    param_num = int.from_bytes(tbl_data[new_offset : new_offset + 4], byteorder = 'little')
    new_offset += 4
    param_table = []

    for _ in range(param_num):
        param_name_size = tbl_data[new_offset]
        param_name = tbl_data[new_offset + 1 : new_offset + 1 + param_name_size].decode('utf-8')
        new_offset += param_name_size + 1
        param_table.append({'Param name': param_name})

    for _ in range(param_num):
        param_table[_]['Unknown value'] = tbl_data[new_offset]
        new_offset += 1

    for _ in range(param_num):
        param_table[_]['Type'] = tbl_data[new_offset]
        new_offset += 1

    if list(tbl_data[new_offset : new_offset + 4]) != [2, 0, 0, 0]:
        print('Error: param table closer check failed')
        return 0
    
    new_offset += 4

    #Raw data
    data = []

    for _ in range(size):

        data.append({})

        for param in param_table:

            if param['Type'] == 1:
                value = signed_byte(tbl_data[new_offset])
                plus_offset = 1

            elif param['Type'] == 8:
                value = int.from_bytes(tbl_data[new_offset : new_offset + 4], byteorder = 'little', signed = True)
                plus_offset = 4

            elif param['Type'] == 11:
                value = struct.unpack('f', tbl_data[new_offset : new_offset + 4])[0]
                plus_offset = 4

            data[-1][param['Param name']] = {'Address': new_offset, 'Value': value, 'Type': param['Type']}
            new_offset += plus_offset

        new_offset += 9

    return data

def randomize_stats(base_stats):

    for item in base_stats:
        if item['_kind_id']['Value'] == 1:
            item['_attack']['Value'] = random.randint(10, 100)
            item['_can_throw_away']['Value'] = random.randint(0, 1)
            if item['_sell_price']['Value'] != -1:
                item['_sell_price']['Value'] = random.randint(10, 150)
            if item['_buy_price']['Value'] != -1:
                item['_buy_price']['Value'] = random.randint(20, 300)

        elif item['_kind_id']['Value'] == 2:
            choose_wielder = random.randint(0, 4)
            if choose_wielder == 0:
                item['_can_equip_mario']['Value'] = 1
                item['_can_equip_mallow']['Value'] = random.randint(0, 1)
                item['_can_equip_geno']['Value'] = random.randint(0, 1)
                item['_can_equip_kupper']['Value'] = random.randint(0, 1)
                item['_can_equip_peach']['Value'] = random.randint(0, 1)
            elif choose_wielder == 1:
                item['_can_equip_mallow']['Value'] = 1
                item['_can_equip_mario']['Value'] = random.randint(0, 1)
                item['_can_equip_geno']['Value'] = random.randint(0, 1)
                item['_can_equip_kupper']['Value'] = random.randint(0, 1)
                item['_can_equip_peach']['Value'] = random.randint(0, 1)
            elif choose_wielder == 2:
                item['_can_equip_geno']['Value'] = 1
                item['_can_equip_mallow']['Value'] = random.randint(0, 1)
                item['_can_equip_mario']['Value'] = random.randint(0, 1)
                item['_can_equip_kupper']['Value'] = random.randint(0, 1)
                item['_can_equip_peach']['Value'] = random.randint(0, 1)
            elif choose_wielder == 3:
                item['_can_equip_kupper']['Value'] = 1
                item['_can_equip_mallow']['Value'] = random.randint(0, 1)
                item['_can_equip_geno']['Value'] = random.randint(0, 1)
                item['_can_equip_mario']['Value'] = random.randint(0, 1)
                item['_can_equip_peach']['Value'] = random.randint(0, 1)
            else:
                item['_can_equip_peach']['Value'] = 1
                item['_can_equip_mallow']['Value'] = random.randint(0, 1)
                item['_can_equip_geno']['Value'] = random.randint(0, 1)
                item['_can_equip_kupper']['Value'] = random.randint(0, 1)
                item['_can_equip_mario']['Value'] = random.randint(0, 1)

            if item['_sell_price']['Value'] != -1:
                item['_sell_price']['Value'] = random.randint(3, 350)
            if item['_buy_price']['Value'] != -1:
                item['_buy_price']['Value'] = random.randint(7, 100)
            item['_can_throw_away']['Value'] = random.randint(0, 1)

            if random.randint(0, 9) == 0:
                item['_resist_element_per']['Value'] = random.randint(1, 2) * 50

            for param in ['_invalid_fear', '_invalid_poison', '_invalid_sleep', '_invalid_silent', '_invalid_mashroom', '_invalid_scarecrow']:
                item[param]['Value'] = 1 if random.randint(0, 9) == 0 else 0

            item['_speed']['Value'] = random.randint(-50, 50)
            item['_attack']['Value'] = random.randint(-50, 75)
            item['_defense']['Value'] = random.randint(-10, 70) if random.randint(0, 20) == 0 else random.randint(100, 150)
            item['_magic_attack']['Value'] = random.randint(-50, 75)
            item['_magic_defense']['Value'] = random.randint(-10, 70) if random.randint(0, 20) == 0 else random.randint(100, 150)

        elif item['_kind_id']['Value'] == 3:
            choose_wielder = random.randint(0, 4)
            if choose_wielder == 0:
                item['_can_equip_mario']['Value'] = 1
                item['_can_equip_mallow']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_geno']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_kupper']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_peach']['Value'] = 1 if random.randint(0, 3) != 0 else 0
            elif choose_wielder == 1:
                item['_can_equip_mallow']['Value'] = 1
                item['_can_equip_mario']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_geno']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_kupper']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_peach']['Value'] = 1 if random.randint(0, 3) != 0 else 0
            elif choose_wielder == 2:
                item['_can_equip_geno']['Value'] = 1
                item['_can_equip_mallow']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_mario']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_kupper']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_peach']['Value'] = 1 if random.randint(0, 3) != 0 else 0
            elif choose_wielder == 3:
                item['_can_equip_kupper']['Value'] = 1
                item['_can_equip_mallow']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_geno']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_mario']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_peach']['Value'] = 1 if random.randint(0, 3) != 0 else 0
            else:
                item['_can_equip_peach']['Value'] = 1
                item['_can_equip_mallow']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_geno']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_kupper']['Value'] = 1 if random.randint(0, 3) != 0 else 0
                item['_can_equip_mario']['Value'] = 1 if random.randint(0, 3) != 0 else 0

            if item['_sell_price']['Value'] != -1:
                item['_sell_price']['Value'] = random.randint(3, 999)
            if item['_buy_price']['Value'] != -1:
                item['_buy_price']['Value'] = random.randint(28, 145)
            if item['_kaeru_coin_price']['Value'] != -1:
                item['_kaeru_coin_price']['Value'] = random.randint(22, 50)
            item['_can_throw_away']['Value'] = random.randint(0, 1)

            if random.randint(0, 6) == 0:
                item['_resist_element_per']['Value'] = random.randint(1, 2) * 50

            for param in ['_invalid_fear', '_invalid_poison', '_invalid_sleep', '_invalid_silent', '_invalid_mashroom', '_invalid_scarecrow', '_invalid_instant_death']:
                item[param]['Value'] = 1 if random.randint(0, 6) == 0 else 0
            
            item['_speed']['Value'] = random.randint(-5, 30)
            item['_attack']['Value'] = random.randint(-30, 45)
            item['_defense']['Value'] = random.randint(-30, 45)
            item['_magic_attack']['Value'] = random.randint(-30, 45)
            item['_magic_defense']['Value'] = random.randint(-30, 45)

    return base_stats

def rebuild_file(tbl):

    with open(tbl, 'rb') as file:
        base_data = file.read()

    base_stats = get_stats(tbl)

    # do stuff with stats

    new_stats = randomize_stats(base_stats)

    # rebuild

    new_data = bytearray(base_data)

    for item in new_stats:
        for param in item:
            if item[param]['Type'] == 8:
                for i in range(4):
                    new_data[item[param]['Address'] + i] = bytearray(int.to_bytes(item[param]['Value'], length = 4, byteorder = 'little', signed = True))[i]
            elif item[param]['Type'] == 1:
                new_data[item[param]['Address']] = item[param]['Value']
            elif item[param]['Type'] == 11:
                for i in range(4):
                    new_data[item[param]['Address'] + i] = bytearray(struct.pack("!f", item[param]['Value']))[i]

    with open(tbl.replace('tbl/', 'Randomizer 1.0.0/romfs/Data/StreamingAssets/data_tbl/'), 'wb') as new_file:
        new_file.write(new_data)

    with open(tbl.replace('tbl/', '').replace('.tbl', '_new_stats.json'), 'w') as json_file:
        json_file.write(json.dumps(new_stats, indent = 2))

rebuild_file('tbl/stella_item_list.tbl')