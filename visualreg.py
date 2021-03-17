from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import os
import sys
import time 
from PIL import Image
from io import BytesIO
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys

STAGING_URL = 'https://uat.lexus.com.au/contact/request-a-test-drive'
PRODUCTION_URL = 'https://www.lexus.com.au/contact/request-a-brochure'
CHROME_PATH = '/Users/dineshpandiyan/Downloads/chromedriver'
IMAGE_SAVE = '/Users/dineshpandiyan/Desktop/Defects/screenshots/'
STAGING_PNG =  '/Users/dineshpandiyan/Desktop/Defects/screenshots/screen_staging.png'
PROD_PNG =  '/Users/dineshpandiyan/Desktop/Defects/screenshots/screen_production.png'
RESULT_IMG = '/Users/dineshpandiyan/Desktop/Defects/screenshots/result.png'

class ScreenAnalysis:    

    driver = None

    def __init__(self):
        self.set_up()
        self.capture_screens()
        self.analyze()
        self.clean_up()

    def set_up(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path=CHROME_PATH,chrome_options=options)

    def clean_up(self):
        self.driver.close()

    def capture_screens(self):
        self.screenshot(STAGING_URL, 'screen_staging.png')
        self.screenshot(PRODUCTION_URL, 'screen_production.png')

    def screenshot(self, url, file_name):
        print("Capturing", url, "screenshot as", file_name, "...")
        self.driver.maximize_window()
        self.driver.get(url)
        height, width = self.scroll_down(self.driver)
        time.sleep(10)
        self.driver.set_window_size(width, height)
        #self.driver.save_screenshot("/Users/dineshpandiyan/Desktop/Defects/screenshots/"+file_name)
        #self.driver.get_screenshot_as_png()
        #print ("Done.")
        #element1 = "//div[contains(@class,'css-16pqwjk-indicatorContainer react-select__indicator react-select__clear-indicator')]//*[contains(@class,'css-19bqh2r')]"
        #element2 = "//input[@id='react-select-6-input']"

        #if self.check_exists_by_xpath(element1): 
        #    self.driver.find_element_by_xpath(element1).click()

        #self.driver.find_element_by_xpath(element2).send_keys("3128")
        #time.sleep(2)
        #self.driver.find_element_by_xpath(element2).send_keys(Keys.ENTER)

        img_binary = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(img_binary))
        img.save(IMAGE_SAVE+file_name)
        # print(file_name)
        print(" screenshot saved ")
    
    def scroll_down(self, driver):
        total_width = driver.execute_script("return document.body.offsetWidth")
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = driver.execute_script("return document.body.clientWidth")
        viewport_height = driver.execute_script("return window.innerHeight")

        rectangles = []

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height

            if top_height > total_height:
                top_height = total_height

            while ii < total_width:
                top_width = ii + viewport_width

                if top_width > total_width:
                    top_width = total_width

                rectangles.append((ii, i, top_width, top_height))

                ii = ii + viewport_width

            i = i + viewport_height

        previous = None
        part = 0

        for rectangle in rectangles:
            if not previous is None:
                driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                time.sleep(0.5)
            # time.sleep(0.2)

            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            previous = rectangle

        return (total_height, total_width)

    def analyze(self):
        screenshot_staging = Image.open(STAGING_PNG)
        screenshot_production = Image.open(PROD_PNG)
        columns = 60
        rows = 80
        screen_width, screen_height = screenshot_staging.size

        block_width = ((screen_width - 1) // columns) + 1 # this is just a division ceiling
        block_height = ((screen_height - 1) // rows) + 1

        for y in range(0, screen_height, block_height+1):
            for x in range(0, screen_width, block_width+1):
                region_staging = self.process_region(screenshot_staging, x, y, block_width, block_height)
                region_production = self.process_region(screenshot_production, x, y, block_width, block_height)

                if region_staging is not None and region_production is not None and region_production != region_staging:
                    draw = ImageDraw.Draw(screenshot_staging)
                    draw.rectangle((x, y, x+block_width, y+block_height), outline = "red")

        screenshot_staging.save(RESULT_IMG)

    def process_region(self, image, x, y, width, height):
        region_total = 0

        # This can be used as the sensitivity factor, the larger it is the less sensitive the comparison
        factor = 150

        for coordinateY in range(y, y+height):
            for coordinateX in range(x, x+width):
                try:
                    pixel = image.getpixel((coordinateX, coordinateY))
                    region_total += sum(pixel)/4
                except:
                    return

        return region_total/factor

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

ScreenAnalysis()
