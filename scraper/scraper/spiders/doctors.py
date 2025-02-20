from typing import Any, List, Tuple

import scrapy
from scrapy import Request
from scrapy.http.response import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class DoctorsSpider(scrapy.Spider):
    name = "doctors"
    allowed_domains = ["www.vezeeta.com"]
    start_urls = ["https://www.vezeeta.com/en/doctor/all-specialities/egypt"]

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.make_driver()

    def parse(self, response: Response):
        links = response.css('a:has(h4)')
        for link in links:
            href = link.css('a::attr(href)').get()
            if href:
                yield Request(
                    url=response.urljoin(href),
                    callback=self.parse_page,
                    dont_filter=True,
                )

    def parse_page(self, response: Response):
        self.driver.get(response.url)
        doctor_name = self.get_doctor_name(response)
        specialities = self.get_specialities(response)
        address = self.get_address(response)
        fees = self.get_fees(response)
        appointment = self.get_appointment()

        yield {
            "name": doctor_name,
            "specialities": specialities,
            "address": address,
            "fees": fees,
            "appointment": appointment,
        }


    def get_doctor_name(self, response: Response) -> str | None:
        return response.xpath('//h3/span/text()').extract_first()

    def get_specialities(self, response: Response) -> str:
        specialities = "".join(response.xpath("//h2/text()").extract())
        additional_sepcialities = response.xpath("//span/h3/a/text()").extract()
        return specialities + ", ".join(additional_sepcialities)

    def get_address(self, response: Response) -> str | None:
        return response.xpath("//span[@itemprop='address']/text()").extract_first()

    def get_fees(self, resposne: Response) -> str | None:
        return resposne.xpath("//span[@itemprop='priceRange']/text()").extract_first()

    def get_appointment(self) -> str | None:
        appointments = []
        data = self.get_elements(locator=(By.CSS_SELECTOR, "div[data-testid='schedule-day--undefined']"))
        if data is None:
            return None

        for lines in data:
            lines = lines.text.split("\n")
            for i in range(0, len(lines), 4):
                try:
                    date = lines[i].strip()
                    start_time = lines[i+1].replace("From", "").strip()
                    end_time = lines[i+2].replace("To", "").strip()
                    appointments.append(f"{date} {start_time} - {end_time}")
                except:
                    continue

        return "\n".join(appointments)

    def make_driver(self) -> None:
        options = Options()
        options.add_argument("--lang=en")
        # options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, timeout=10)


    def get_element(self, locator: Tuple[str, str]) -> str | None:
        try:
            return self.wait.until(EC.presence_of_element_located(locator)).text
        except:
            return None

    def get_elements(self, locator: Tuple[str, str]) -> List | None:
        try:
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except:
            return None

    def click_element(self, locator: Tuple[str, str]) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located(locator)).click()
            return True
        except:
            return False
