# %%
from selenium import webdriver
import pandas as pd
from sqlalchemy import create_engine
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# %% [markdown]
# #Variables

# %%
page = 1
url = 'https://zyntern.com/jobs?page='+str(page)
hirdetesLeiras = {
    'Indicator': [],
    'ceg': [],
    'pozicio': [],
    'skills': [],
    'soft skills': [],
    'details': [],
    'bottom-location': [],
    'link': []
}
databasename = str(pd.to_datetime("today").date()) + ' zynter_com.db'
engine = create_engine('sqlite:///' + databasename, echo=False)


# %%

chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)  # options=chrome_options
driver.get(url)

# %% [markdown]
# # A szükséges információk összegyüjtése.

# %%
allasokSzama = driver.find_elements(By.TAG_NAME, 'h1')[0].text  # állások száma

# %% [markdown]
# # Fügvény a declarált dict feltöltésére a kinyert adatokkal.

# %%


def dictappend(hirdetesekKontener):
    for i in range(len(hirdetesekKontener)):
        indexincrement = len(hirdetesLeiras['Indicator'])
        hirdetesLeiras['Indicator'].append(indexincrement)
        hirdetesLeiras['link'].append(
            hirdetesekKontener[i].get_attribute('href'))
        job = hirdetesekKontener[i].find_elements_by_xpath('./div')
        ceg = hirdetesekKontener[i].find_elements_by_xpath('./div/h5')[0]
        poz = hirdetesekKontener[i].find_elements_by_xpath('./div/h3')[0]
        skills = hirdetesekKontener[i].find_elements(
            By.XPATH, './div/div[1]/span')
        softSkills = hirdetesekKontener[i].find_elements(
            By.XPATH, './div/div[2]/span')
        for j in range(len(job)):
            if job[j].get_attribute('class') == 'info':
                hirdetesLeiras['ceg'].append(ceg.text)
                hirdetesLeiras['pozicio'].append(poz.text)
                fs = ""
                fss = ""
                for i in range(len(skills)):
                    fs += skills[i].text
                hirdetesLeiras['skills'].append(fs)
                for i in range(len(softSkills)):
                    fss += softSkills[i].text
                hirdetesLeiras['soft skills'].append(fss)
            elif job[j].get_attribute('class') == 'details':
                hirdetesLeiras['details'].append(
                    job[j].text.replace("\n", " "))
            elif job[j].get_attribute('class') == 'bottom-location':
                hirdetesLeiras['bottom-location'].append(job[j].text)

# %% [markdown]
# # Az oldal megnyitása , a poziciók adatainak kigyüjtése , majd oldalváltás


# %%
# Az oldalon addig lapozni amig az utolsó oldalt el nem éri .
nincstobboldal = driver.find_elements(
    By.XPATH, "//*[contains(text() , 'Nincs találat')]")


while len(nincstobboldal) == 0:
    url2 = 'https://zyntern.com/jobs?page='+str(page)
    driver.get(url2)
    driver.implicitly_wait(5)
    hirdetesekKontener = driver.find_elements(
        By.CSS_SELECTOR, '#job_listing_container > div > div > div.listings>a')
    dictappend(hirdetesekKontener)
    page = page+1
    nincstobboldal = driver.find_elements(
        By.XPATH, "//*[contains(text() , 'Nincs találat')]")
    print(url2)
    print(f"Eddig kinyert adat : {len(hirdetesLeiras['Indicator'])} ")
print(
    f"Az oldalon talált állások száma : {allasokSzama} ebből a mennyiségből kinyert addat : {len(hirdetesLeiras['Indicator'])} ")

# %% [markdown]
# # A kinyert addat mentése XLSX és SQLlite3 db formátumba.

# %%
df = pd.DataFrame(hirdetesLeiras)
df = df.drop('Indicator', axis=1)
df.to_excel(str(pd.to_datetime("today").date()) + ' zyntern_com.xlsx')
df.to_sql('hirdetesLeiras', con=engine, if_exists='append')
driver.quit()
