import locale
# Set the locale to default 'C' locale
locale.setlocale(locale.LC_ALL, '')
# Define a function to the format the currency string
def format_currency(amount):
    return '${:,.2f}'.format(amount)
