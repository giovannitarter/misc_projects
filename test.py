
import xlrd
import re
import sys


class Price(object):

    def __init__(self, code, start_row, name):
        self.code = code
        self.components = []
        self.description = ""
        self.start_line = start_row
        self.name = name
        self.costs = []
    


if __name__ == "__main__":
    
    book = xlrd.open_workbook(sys.argv[1])
    print("The number of worksheets is {0}".format(book.nsheets))
    print("Worksheet name(s): {0}".format(book.sheet_names()))
    sh = book.sheet_by_index(6)
    
    prices = []
   
    to_skip = 0
    c_price = None
    for idx,l in enumerate(sh.col(0)):

        if to_skip > 0:
            to_skip = to_skip - 1
            continue

        if l.ctype != 0:
            
            fields = l.value.split(".")
            fields_nr = len(fields)
            
            if re.match("[A-Z]\.[0-9]+\.[0-9]+\.[0-9]+$", l.value) is not None:
                name = sh.cell(idx, 1).value
                c_price = Price(l.value, idx, name)
                prices.append(c_price)

            elif re.match("[A-Z]\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\**", l.value) is not None:
                c_price.components.append(l.value)
                name = sh.cell(idx, 1).value
                rows = []
                for i in range(3, 20):
                    row = sh.row(idx+i)
                    non_empty = [ x for x in row if x.ctype != 0 ]
                    if non_empty == []:
                        break
                    else:
                        rows.append(((idx + i), row))

                    to_skip = i
                
                for row_nr, r in rows:
                    price_cells = r[13:15]
                    
                    cost_type = "int"
                    if r[13].ctype == 2:
                        cost_type = "est"
                    else:
                        cost_type = "int"

                    price_cells = [ x for x in price_cells if x.ctype != 0 ]
                    if price_cells != []:
                        if price_cells[0].ctype == 2:
                            val = price_cells[0].value
                            if val != 0:
                                c_price.costs.append((row_nr, r[1].value, cost_type, val))
                
            else:
                c_price.description = l.value
    

    tot_int = 0
    tot_est = 0

    for p in prices:
        print("\nline: {} -> {} {}".format(p.start_line, p.code, p.name))
        print("description: {}".format(p.description[0:80]))
        print("costs:")
        for p in p.costs:
            print("    {}".format(p))
            if p[2] == "int":
                tot_int = tot_int + p[3]
            elif p[2] == "est":
                tot_est = tot_est + p[3]


    print(tot_int)
    print(tot_est)
    

