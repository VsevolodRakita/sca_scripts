import logging
from SCA_scripts.reading.excel_reader import read_excel_as_list
from SCA_scripts.writing.word_writer import write_to_docx

LRM = "\u200E"

def run(args):
    """
    Main entry point for this module.

    :param args: The arguments for the script.
    """

    logging.info("Analyzing input file: %s", args.input)
    data = read_excel_as_list(args.input)
    data = clean(data)
    out = process(data)
    #print("-----x-----")
    #print(out)
    #print("------x-----")
    if args.output:
        logging.info("Output will be saved to: %s", args.output)
    else:
         logging.info("Output will be saved to: 1.docx")
    write_to_docx(out, args.output)
    logging.debug("Analysis completed successfully.")


def clean(excel_array,first_year=None,last_year=None):
    """
    Cleans a list of lists from a balance sheet.

    :param excel_array: List of lists read from the excell file.
    :param first_year: The first year to be returned in the clean array. Earlyer years will be droped. (default: All years from the beginning).
    :param last_year: The last year to be read. Later years will be droped. (default: All years to the end).
    :return: Clean list of lists
    """
    rows = 0
    while rows< len(excel_array) and rows<50 and excel_array[rows][0]!='סה"כ הון עצמי':
        rows+=1
    if rows==len(excel_array) or rows==50:
        print("bad")
    cols=1
    first_col=1
    while excel_array[0][cols]:
        if not excel_array[0][cols].is_integer():
            break
        n = int(excel_array[0][cols])
        if last_year and n>last_year:
            break
        if first_year and n<first_year:
            first_col+=1
        cols+=1

    out = [[row[0]] + row[first_col:cols] for row in excel_array[:rows+1]]
    aux=[]
    for i,row in enumerate(out):
        if row[0]=='סה"כ התחייבויות' or row[0]=='סה"כ נכסים':
            aux.append(i)
    for i in reversed(aux):
        out.pop(i)
    return out

def process(arr):
    """
    Processes a clean array from a balance sheet for printing.

    :param arr: Clean list of lists.
    :return: String for printing.
    """
    out=""
    i=1
    years = [str(x) for x in arr[0]]
    while i< len(arr):
        while i< len(arr) and arr[i][1] is None:
            i+=1
        j=i
        while j< len(arr) and arr[j][1] is not None:
            j+=1
        out+=process_one(years, arr, i-1, j)
        out+="\n \n"
        i=j+1
    return out
        


def process_one(years,arr,i,j):
    """
    Processes one part of the balanced sheet (Current Assets, etc.).

    :param years: A list of strings representing the years in the balance sheet.
    :param arr: Clean array from a balance sheet.
    :param i: The first index of the part in arr.
    :param j: The index right after the end of the part.
    :return: String sumerizing the part.
    """
    if arr[i][0] is None:
        return handle_capital(arr[i+1], years)
    name = arr[j-1][0]
    name = name[5:] #delets the סה"כ
    out = "ה"+name+" של החברה מורכבים מ"
    for k in range(i+1,j-1):
        out+=arr[k][0]+f",{LRM} "
    out = out[:-3]+f".{LRM}"
    out+="\n"
    if len(arr[j-1])==4:
        out+=handle_three_years(arr, i, j, years, name)
    else:
        out+=handle(arr, i, j, years, name)
    return out

def handle(arr, i, j, years, name):
    '''
    A helper function for process_one. Creats the output string in case the number of years is different than 3 and the part is not
    the capital.

    :param arr: Clean array from a balance sheet.
    :param i: The first index of the part in arr.
    :param j: The index right after the end of the part.
    :param years: A list of strings representing the years in the balance sheet.
    :return: String sumerizing the part.
    '''
    updown = []
    cause = ""
    temp =[arr[k] for k in range(i+1,j)]
    while temp[-1][0].startswith('סה"כ'):
        temp.pop(-1)
    out = f'בשנת {years[1]} ה{name} של החברה הסתכמו לסך של כ-{LRM} {round(arr[j-1][1])}{LRM} אלפי ש"ח.{LRM} '
    for k in range(2,len(years)):
        if round(arr[j-1][k])> round(arr[j-1][k-1]):
            updown = ["גדלו", "הגידול", "גידול"]
            cause=max(temp, key= lambda row: row[k]-row[k-1])[0]  
        else:
            updown = ["קטנו", "הקיטון", "קיטון"]
            cause = max(temp, key= lambda row: row[k-1]-row[k])[0]
        out+= f'בשנת {years[k]} ה{name} של החברה {updown[0]} לסך של כ-{LRM} {round(arr[j-1][k])}{LRM} אלפי ש"ח.{LRM} {updown[1]} נרשם עקב {updown[2]} בסעיף {cause}.{LRM} '
    out+='\n'
    return out

def handle_three_years(arr, i, j, years, name):
    '''
    A helper function for process_one. Creats the output string in case the number of years is  3.

    :param arr: Clean array from a balance sheet.
    :param i: The first index of the part in arr.
    :param j: The index right after the end of the part.
    :param years: A list of strings representing the years in the balance sheet.
    :return: String sumerizing the part.
    '''
    first = []
    cause_first = ""
    second = []
    cause_second = ""
    temp =[arr[k] for k in range(i+1,j)]
    while temp[-1][0].startswith('סה"כ'):
        temp.pop(-1)
    if round(arr[j-1][2])> round(arr[j-1][1]):
        first = ["גדלו", "הגידול", "גידול"]
        cause_first = max(temp, key= lambda row: row[2]-row[1])[0]       
    else:
        first = ["קטנו", "הקיטון", "קיטון"]
        cause_first = max(temp, key= lambda row: row[1]-row[2])[0]
    if round(arr[j-1][3])> round(arr[j-1][2]):
        second = ["גדלו", "הגידול", "גידול"]
        cause_second = max(temp, key= lambda row: row[3]-row[2])[0]    
    else:
        second = ["קטנו", "הקיטון", "קיטון"]
        cause_second = max(temp, key= lambda row: row[2]-row[3])[0]
    return f'בשנת {years[2]} ה{name} של החברה {first[0]} לסך של כ-{LRM} {round(arr[j-1][2])}{LRM} אלפי ש"ח בהשוואה לסך של כ-{LRM} {round(arr[j-1][1])}{LRM} ש"ח בשנת{LRM} {LRM}{years[1]}{LRM}.{LRM} {first[2]} התרחש בעיקר עקב {first[1]} בסעיף {cause_first}.{LRM} בשנת {years[3]} ה{name} של החברה {second[0]} לסך של כ-{LRM} {round(arr[j-1][3])}{LRM} אלפי ש"ח.{LRM} {second[1]} התרחש בעיקר עקב {second[2]} בסעיף {cause_second}.{LRM}\n'

def handle_capital(row, years):
    '''
    A helper function for process_one. Creats the output string in case the part is the capital.

    :param row: The row from the excel file describing the capital.
    :param years: A list of strings representing the years in the balance sheet.
    :return: String sumerizing the capital.
    '''
    
    i=1
    out=""
    while i< len(row):
        if round(row[i])>0:
            out += f'בשנת {LRM}{years[i]}{LRM} {LRM}ההון העצמי של החברה הסתכם לסך של כ-{LRM} {LRM}{round(row[i])}{LRM} אלפי ש"ח.{LRM} '
        elif round(row[i])<0:
            out += f'בשנת {LRM}{years[i]}{LRM} נרשם גרעון בהון העצמי בסך של כ-{LRM} {LRM}{-round(row[i])}{LRM} אלפי ש"ח.{LRM} '
        else:
            out += f'בשנת {LRM}{years[i]}{LRM} לא נרשם הון עצמי מהותי.{LRM} '
        i+=1    
    return out


if __name__ == "__main__":
    from SCA_scripts.reading.excel_reader import read_excel_as_list
    file_path = "C:\\coding projects\\sca_scripts\\tests\\1.xlsx"  
    data = read_excel_as_list(file_path)
    data = clean(data)
    process(data)