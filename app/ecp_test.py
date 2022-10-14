ss = """Phone = +77778944349
E = novosel5510@mail.ru
SN = КАНТАЕВ
SERIALNUMBER = IIN860518351108
G = МУРАТБЕКОВИЧ
CN = КАНТАЕВ НАЗЫМБЕК
OU = BIN981240001783
S = Северо-Казахстанская область
O = "Отдел внутренней политики; культуры; чего-то там; капусты и развития языков Акжарского района Северо-Казахстанской област"
C = KZ"""

ss = ss.split('\n')
ss.reverse()
# print(ss)
print(','.join(ss).replace('Phone = ', '2.5.4.20=\\').replace(
            ' = ', '=').replace(' , ', ',').replace('\r', '').replace('SN=', 'SURNAME=').replace('"','\\"'))