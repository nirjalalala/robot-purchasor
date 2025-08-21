from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

import os

@task
def order_robots_from_RobotSpareBin():
    '''
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a pdf file
    Saves the screenshot of the ordered robot
    Embeds the screenshot of the robot to the PDF receipt
    Creates ZIP archive of the receipts and the images
    '''
    browser.configure(slowmo=10)
    open_robot_order_website()
    orders = get_orders()
    
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        store_receipt_as_pdf(row['Order number'])
        order_another()

    archive_pdfs()


def open_robot_order_website():
    '''Naviage to the given url'''
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    ''' Download orders file, read it as a table and return the result  '''
    http=HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    table= tables.read_table_from_csv("orders.csv")
    return table

def close_annoying_modal():
    '''Presses the 'OK' button'''
    page = browser.page()
    page.click("text=OK")

def fill_the_form(row):
    '''Fill data to input elemnts in the form'''
    page= browser.page()
    page.select_option("#head", row['Head'])
    page.click("#id-body-" + str(row["Body"]) )
    page.fill("input[type='number'][required]",row['Legs'])
    page.fill("#address",row["Address"])
    page.click("#preview")
    while True:
        page.click("#order")
        if page.locator(".alert-danger").is_visible():
            continue
        else:
            break

def order_another():
    page= browser.page()
    page.click("text=Order Another Robot")

def store_receipt_as_pdf(order_number):
    '''Exports the pdf of each order'''
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf=PDF()
    os.makedirs("output", exist_ok=True)
    screenshot_robot(order_number)
    pdf.html_to_pdf(receipt, f"output/{order_number}.pdf")
    pdf.add_files_to_pdf(
        files=[f'output/{order_number}.png'],
        target_document = f'output/{order_number}.pdf',append=True
    )

def screenshot_robot(order_number):
    page = browser.page()
    os.makedirs("output", exist_ok=True)
    image = page.locator("#robot-preview-image").screenshot(path=f'output/{order_number}.png')

def archive_pdfs():
    '''Archive all pdfs to a single folder'''
    archive = Archive()
    archive.archive_folder_with_zip(
        folder='output',
        archive_name='output/orders.zip',
        include="*pdf"
    )