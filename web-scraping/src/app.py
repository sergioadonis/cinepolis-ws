from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import presence_of_element_located, visibility_of_element_located
from selenium.webdriver.support.ui import WebDriverWait


def set_chrome_options():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def get_movie_id_list(driver, wait):
    driver.get("https://www.cinepolis.com.sv/cartelera")

    '''
    cities = ["San Salvador", "Santa Ana"]
    cinemas_choice = "Todos los cines"

    for city in cities:
        cityBillboardSearch_xpath = '//*[@id="header"]/section[1]/section/div[1]/div[1]'
        cityBillboardSearch = wait.until(
            presence_of_element_located((By.XPATH, cityBillboardSearch_xpath)))

        cityBillboardSearch.click()

        city_dropdown_xpath = '/html/body/div[2]'
        wait.until(visibility_of_element_located(
            (By.XPATH, city_dropdown_xpath)))
        cities_ul_xpath = '/html/body/div[2]/div[1]/div[1]/ul'
        cities_ul = wait.until(
            presence_of_element_located((By.XPATH, cities_ul_xpath)))
        for li in cities_ul.find_elements_by_tag_name("li"):
            print(li.text)
    '''

    billboard_xpath = '//*[@id="main-app"]/div/div[5]/section[5]/div/div'
    billboard_div = wait.until(
        presence_of_element_located((By.XPATH, billboard_xpath)))

    movie_id_list = []

    for div in billboard_div.find_elements_by_tag_name("div"):
        div_id = div.get_attribute("id")
        if len(div_id) > 0:
            movie_id_list.append(div_id)

    return movie_id_list


def get_movie_details(driver, wait, movie_id):
    driver.get("https://www.cinepolis.com.sv/cartelera")
    movie_div = wait.until(presence_of_element_located((By.ID, movie_id)))
    # print(movie_div.get_attribute("class"))
    movie_div.find_element_by_class_name("poster").click()

    movie_details_xpath = '//*[@id="main-app"]/div/div[5]/div/div[2]/section'
    movie_details_div = wait.until(
        presence_of_element_located((By.XPATH, movie_details_xpath)))

    h1 = movie_details_div.find_element_by_tag_name("h1")
    title = h1.text
    print(title)
    h6 = movie_details_div.find_element_by_tag_name("h6")
    #span = h6.find_element_by_tag_name("span")
    subtitle = h6.text  # + " " + span.text
    print(subtitle)
    print(driver.current_url)

    shedules_xpath = '//*[@id="main-app"]/div/div[5]/div/div[2]/section/div[2]/div[2]/div[1]/div/div[4]/ul'
    shedules_ul = wait.until(
        presence_of_element_located((By.XPATH, shedules_xpath)))

    # print(shedules_ul.get_attribute("class"))
    print(len(shedules_ul.find_elements_by_tag_name("li")))

    first_li_xpath = '//*[@id="main-app"]/div/div[5]/div/div[2]/section/div[2]/div[2]/div[1]/div/div[4]/ul/li[1]'
    wait.until(
        presence_of_element_located((By.XPATH, first_li_xpath)))

    print(len(shedules_ul.find_elements_by_tag_name("li")))

    for li in shedules_ul.find_elements_by_tag_name("li"):
        # print(li.get_attribute("class"))
        h3 = li.find_element_by_tag_name("h3")
        print(h3.text)


if __name__ == "__main__":
    chrome_options = set_chrome_options()

    movie_id_list = []

    with webdriver.Chrome(options=chrome_options) as driver:
        # Do stuff with your driver
        wait = WebDriverWait(driver, 60)
        movie_id_list = get_movie_id_list(driver, wait)

    print(movie_id_list)
    # movie_id_list = ['getTicket_3102']

    # for movie_id in movie_id_list:
    #     with webdriver.Chrome(options=chrome_options) as driver:
    #         # Do stuff with your driver
    #         wait = WebDriverWait(driver, 60)
    #         movie_details = get_movie_details(driver, wait, movie_id)

    # driver.close()
