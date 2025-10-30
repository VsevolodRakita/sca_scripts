import openpyxl

def read_excel_as_list(file_path, sheet_name=None):
    """
    Reads an Excel file and returns its rows as a list of lists.

    :param file_path: Path to the Excel file (.xlsx)
    :param sheet_name: Name of the sheet to read (default: active sheet)
    :return: List of lists containing rows
    """
    # Load the workbook
    workbook = openpyxl.load_workbook(file_path, data_only=True)

    # Select sheet
    if sheet_name:
        sheet = workbook[sheet_name]
    else:
        sheet = workbook.active

    # Extract rows
    rows = []
    for row in sheet.iter_rows(values_only=True):
        rows.append(list(row))

    return rows
