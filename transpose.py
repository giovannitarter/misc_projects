
import xlrd
import re
import sys


class Price(object):

    def __init__(self, code, start_row, name, description):
        self.code = code
        self.components = []
        self.description = str(description)
        self.start_line = start_row
        self.name = name
        self.costs = []
   

def parse_categories(sh):
   
    int_cat = {}
    ext_cat = {}

    row = sh.row(0)

    for idx in range(16,21):
        cell = row[idx]
        int_cat[idx] = cell.value

    for idx in range(22,28):
        cell = row[idx]
        if cell.ctype != 0:
            ext_cat[idx] = cell.value
    
    print("")
    print(int_cat)
    print(ext_cat)

    return int_cat, ext_cat
    

def transpose(start, end, header_row, line_to_price):
    
    headers = {}
    cat_to_prices = {}
    
    for cat in range(start, end):
        header = sh.cell(header_row, cat).value
        header.replace("\n", " ")
        headers[cat] = header

        prices_list = cat_to_prices.get(cat, [])
        cat_to_prices[cat] = prices_list
    
        for idx, cell in enumerate(sh.col(cat)):
            if cell.ctype == 2:
                if idx in line_to_price.keys():
                    prices_list.append(line_to_price[idx])
    res = {}
    for hd in headers:
        res[headers[hd]] = cat_to_prices[hd]

    return res


def print_matrix(mat):
    for r in mat:
        print(r)
        price_sum = 0
        for price in mat[r]:
            print(" > {}".format(price))
            price_sum = price_sum + price[1][3]
        print("sum: {}".format(price_sum))


def parse_prices(sheet):

    sh = sheet
    prices = []
    to_skip = 0
    c_price = None
    for idx, l in enumerate(sh.col(0)):

        if to_skip > 0:
            to_skip = to_skip - 1
            continue

        if l.ctype != 0:
            
            ##cerca codice prezzo su prima colonna e imposta cprice
            if re.match(
                    "[A-Z]\.[0-9]+\.[0-9]+\.[0-9]+[.0-9]*\**$", 
                    l.value
                    ) is not None:

                code = sh.cell(idx, 0).value
                name = sh.cell(idx, 1).value
                description = sh.cell(idx, 2).value
                c_price = Price(l.value, idx, name, description)
                prices.append(c_price)
                
                rows = []
                for idx2 in range(3, 25):
                    row = sh.row(idx + idx2)
                    row_non_empty = [ x for x in row if x.ctype != 0 ]
                    if len(row_non_empty) == 0:
                        to_skip = idx2
                        break
                    else:
                        rows.append(((idx + idx2 + 1), row))

#                print("working on idx: {}".format(idx))
#                for idx, r in enumerate(rows):
#                    print("{} - {}\n".format(idx, r))
                
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
                                c_price.costs.append(
                                        (
                                            row_nr, 
                                            r[1].value, 
                                            cost_type, 
                                            val
                                            )
                                        )
    return prices



if __name__ == "__main__":
    
    book = xlrd.open_workbook(sys.argv[1])
    print("The number of worksheets is {0}".format(book.nsheets))
    print("Worksheet name(s): {0}".format(book.sheet_names()))
    sh = book.sheet_by_index(6)

    int_cat, ext_cat = parse_categories(sh)
    
    all_cat = {}
    all_cat.update(int_cat)
    all_cat.update(ext_cat)

    
    prices = parse_prices(sh)

    tot_int = 0
    tot_est = 0

    line_to_price = {}

    for p in prices:
        print("\nline: {} -> {} {}".format(p.start_line, p.code, p.name))
        print("description: {}".format(p.description[0:80]))
        print("costs:")
        for c in p.costs:
            print("    {}".format(c))
            if c[2] == "int":
                tot_int = tot_int + c[3]
            elif c[2] == "est":
                tot_est = tot_est + c[3]

            line_to_price[c[0]] = (p.name, c)


    print("prices_nr: {}".format(len(prices)))
    print(tot_int)
    print(tot_est)

