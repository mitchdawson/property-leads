from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from datetime import date, datetime
import time

# URL = "https://rightmove.co.uk/properties/102167105#/"
URL = "https://rightmove.co.uk/properties/85020649#/"

sale_history_button = 'button[class="_1-GJOH09_oTTmLw-B-feOC"]'

sale_table = 'div[class="_1SNP1o4T-Q9HHmHymdO1Gn"]'
old_table_xpath = '//tbody//tr'
table_xpath = '/html/body/div[4]/div/div[3]/main/div[20]/div/div[2]/table/tbody/tr'
new_table_xpath = "//div[@class='_1SNP1o4T-Q9HHmHymdO1Gn']/table/tbody/tr"
year_xpath = ''
# /html/body/div[4]/div/div[3]/main/div[20]/div/div[2]/table/tbody
# /html/body/div[4]/div/div[3]/main/div[20]/div/div[2]/table/tbody/tr[1]
# table =  driver.find_element_by_xpath("//table[@class='datadisplaytable']")
# <table><thead><tr><th>Year sold</th><th>Sold price</th><th>&nbsp;</th></tr></thead><tbody><tr><td>2016</td><td><div><span class="_3tRI_8VCyywxUAbVaZFBNe">£425,000</span></div></td><td><div class="YPgKdkZRT0Tah-_KSPfgP">+315%</div></td></tr><tr><td>1998</td><td><div><span class="_3tRI_8VCyywxUAbVaZFBNe">£102,500</span></div></td><td></td></tr></tbody></table><div class="_1QSdFfgExZ7FRvWnF7wDyB">Source acknowledgement: House price data produced by the Land Registry</div><a class="_1jpwb8BjF0Rw-Zvk0AX36R" target="_blank" href="/house-prices/ig10-3dd.html"><span>Go to nearby sold prices</span><svg role="img" aria-hidden="true"><use xlink:href="#link"></use></svg></a>
# <div class="_1SNP1o4T-Q9HHmHymdO1Gn"><table><thead><tr><th>Year sold</th><th>Sold price</th><th>&nbsp;</th></tr></thead><tbody><tr><td>2016</td><td><div><span class="_3tRI_8VCyywxUAbVaZFBNe">£425,000</span></div></td><td><div class="YPgKdkZRT0Tah-_KSPfgP">+315%</div></td></tr><tr><td>1998</td><td><div><span class="_3tRI_8VCyywxUAbVaZFBNe">£102,500</span></div></td><td></td></tr></tbody></table><div class="_1QSdFfgExZ7FRvWnF7wDyB">Source acknowledgement: House price data produced by the Land Registry</div><a class="_1jpwb8BjF0Rw-Zvk0AX36R" target="_blank" href="/house-prices/ig10-3dd.html"><span>Go to nearby sold prices</span><svg role="img" aria-hidden="true"><use xlink:href="#link"></use></svg></a></div>
# /html/body/div[4]/div/div[3]/main/div[20]/div/div[2]/table/tbody/tr[2]/td[2]/div/span
def main():
    start = datetime.utcnow()
    print(start)
    # Create Some Options for the browser object.
    options = Options()
    # Run in headless mode.
    options.headless = True
    # Create a Firefox Browser Instance
    browser = webdriver.Firefox(options=options)
    # browser = webdriver.Firefox()
    browser.maximize_window()
    browser.get(URL)
    time.sleep(2)
    # print(datetime.utcnow())
    # WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//div[@class='modal-footer']//button[@Class='btn btn-danger x' and text()='Maybe Later']"))).click()
    # browser.find_element_by_css_selector(sale_history_button).click()

    # table =  driver.find_element_by_xpath("//table[@class='datadisplaytable']")
    # table =  driver.find_element_by_xpath("//table[@class='datadisplaytable']")
    # table = browser.find_elements_by_tag_name('tbody')
    # Click to Accept Cookies
    # print("waiting 10")
    # WebDriverWait(browser, 10).until(EC.alert_is_present())
    # alert = browser.switch_to.alert
    # browser.find_element_by_xpath('//button[@class="optanon-allow-all.accept-cookies-button"]').click()
    # browser.implicitly_wait(10)
    # time.sleep(5)
    # print(datetime.utcnow())
    
    cookies = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="optanon-allow-all accept-cookies-button"]')))
    print("clicking cookies")
    cookies.click()
    # print("waiting 5")
    # print(datetime.utcnow())
    # time.sleep(5)
    print("finding sales history")
    # address_history = WebDriverWait(browser, 10).until(EC.element_to_be_clickable(sale_history_button))
    address_history = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH,"//*[@class='_1-GJOH09_oTTmLw-B-feOC']")))
    print("sleeping before clicking address history")
    time.sleep(1)
    address_history.click()
    # browser.find_element_by_css_selector(sale_history_button).click()
    time.sleep(1)
    print("finding table")
    table = browser.find_elements_by_xpath(new_table_xpath)
    print("found table")
    if table:
        # print(len(table))
        for t in table:
            year = t.find_element_by_tag_name('td')
            # year = t.find_element_by_xpath('//td')
            # price = t.find_element_by_xpath("//td//div//span[@class='_3tRI_8VCyywxUAbVaZFBNe']")
            price = t.find_element_by_tag_name('span')
            print(year.text, price.text)
   

    browser.close()
    finish = datetime.utcnow()
    print(finish)
    print(finish - start)

if __name__ == "__main__":
    # for i in range(5):
    main()