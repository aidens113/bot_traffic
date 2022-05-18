import pyautogui
import time
import math
import random
import os
import sys
import requests
import wmi
import imaplib
import email
from email.header import decode_header
import webbrowser
import threading
from os.path import expanduser
import concurrent.futures
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from os.path import expanduser
import concurrent.futures
from datetime import datetime
import time,string,zipfile,os
#import selenium

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
    
#Presses keyboard key
def press_key(key, driver):
    actions = ActionChains(driver)
    actions.send_keys(key)
    actions.perform()

#Random keys using .send_keys method. 
def randkeys(element, keys, driver):
    for myi in keys:
        element.send_keys(myi)
        time.sleep(random.uniform(0.05, 0.25))

#Creates a JS extension to automatically send proxy username and password, since chromedriver Selenium does not have proper auth for proxies 
def create_proxyauth_extension(proxy_host, proxy_port,proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
    """Proxy Auth Extension
    args:
        proxy_host (str): domain or ip address, ie proxy.domain.com
        proxy_port (int): port
        proxy_username (str): auth username
        proxy_password (str): auth password
    kwargs:
        scheme (str): proxy scheme, default http
        plugin_path (str): absolute path of the extension

    return str -> plugin_path
    """
    if plugin_path is None:
        file='./chrome_proxy_helper'
        if not os.path.exists(file):
            os.mkdir(file)
        plugin_path = file+'/%s_%s@%s_%s.zip'%(proxy_username,proxy_password,proxy_host,proxy_port)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = string.Template(
    """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "${scheme}",
                host: "${host}",
                port: parseInt(${port})
              },
              bypassList: ["foobar.com"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "${username}",
                password: "${password}"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    #Zips extension and adds it to browser
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


#Initiate the driver. Great for multi-threading
def initdriver(proxy):
    print(proxy)
    chrome_options = webdriver.ChromeOptions()

    #List of user agents
    mobilerand = random.randint(0,10)
    useragents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
                  ,'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
                  ,'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
                  ,'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
                  ,'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/91.0.4472.80 Mobile/15E148 Safari/604.1'
                  ,'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/91.0.4472.80 Mobile/15E148 Safari/604.1'
                  ,'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36'
                  ,'Mozilla/5.0 (Linux; Android 10; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36']
    devicemetricslist1 = [640,
                          480,
                          768]
    
    devicemetricslist2 = [1136,
                          800,
                          1024]

    #Sets a random mobile user agent
    if mobilerand >= 3:
        metric = random.randint(0,int(len(devicemetricslist1)-1))
        mobile_emulation = {
            "deviceMetrics": { "width": devicemetricslist1[metric], "height": devicemetricslist2[metric], "pixelRatio": 3.0 },
        
        "userAgent": useragents[random.randint(0,int(len(useragents)-1))]}
        #chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    #Set your proxy options
    countries = ['IE','US','UK','CA']
    proxyauth_plugin_path = create_proxyauth_extension(
    proxy_host=str(str(proxy.split(":")[0]).strip().replace("\n","").replace("\r","")), 
    proxy_port=str(str(proxy.split(":")[1]).strip().replace("\n","").replace("\r","")),#80,
    proxy_username=str(str('username-'+str(countries[random.randint(0,int(len(countries)-1))])+'-refreshMinutes-10')),,#"country-ca",
    proxy_password='passw',
    scheme='http'
    )
    chrome_options.add_extension(proxyauth_plugin_path)
    
    driver = webdriver.Chrome(executable_path='chromedriver.exe',options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.delete_all_cookies()
    #driver.set_window_position(-10000,0)
    return driver



#Sets website referrer in request headers
def setreferer(request):
    del request.headers['Referer']
    sources = ['https://google.com','https://instagram.com','https://facebook.com','https://yahoo.ca','https://bing.com','duckduckgo.com'] 
    
    request.headers['Referer'] = sources[random.randint(0,int(len(sources)-1))]


#Clicksubmit dynamic function. Attempts to click a submit button.
def clicksubmit(driver):
    try:
        keywords = ['Get Link','Click here to continue','Accept','accept','Submit','Continue','Go','go','Next','next',">>",">","Start",'start',"Start Now",'Save & Continue','Ok','OK']
        for _ in range(3):
            time.sleep(0.1)
            #Scans page for elements containing the above keywords. Good accuracy, add more keywords for more accuracy.
            for keyword in keywords:
                try:
                    elements = driver.find_elements_by_xpath("//button[ contains (text(), '"+str(keyword)+"' ) ]")
                    for element in elements:
                        try:
                            element.click()
                            return
                        except:
                            try:
                                driver.execute_script("arguments[0].click();", element)
                            
                            except Exception as EEe:
                                print("Error: "+str(EEe))    
                    
                except:
                    try:
                        driver.find_element_by_xpath("//*[ contains (text(), '"+str(keyword)+"' ) ]").send_keys(Keys.SPACE)
                    except Exception as EE:
                        print("Couldn't find yet: "+str(EE))
        for _ in range(3):
            time.sleep(0.1)
            for keyword in keywords:
                try:
                    allinputs = driver.find_elements_by_tag_name('input')
                    for inp in allinputs:
                        if keyword in inp.get_attribute('value'):
                            inp.click()
                            return
                except Exception as EE:
                    print("Error: "+str(EE))
    except Exception as EEeeee:
        print("Error: "+str(EEeeee))

    
    

    #Failsafe
    #try:
        #allforms = driver.find_elements_by_tag_name("form")
        #for form in allforms:
            #form.submit()
    #except Exception as EEe:
     #   print("Error: "+str(EEe))

def go(proxy):
    global urltovisit
    while True:
        try:
            #Initiate driver with proxy
            driver = initdriver(proxy)    
            
            #My example code for a specific use case. Plug and play to fit your needs
            driver.request_interceptor = setreferer
            try:
                driver.get(urltovisit)
            except:
                print("Couldn't fully load page, still continuing")
            time.sleep(random.uniform(2.0,5.0))
            
            for _ in range(50):
                time.sleep(1)
                
                
                print("Len: "+str(len(driver.window_handles)))
                
                if (len(driver.window_handles) >= 2):
                    driver.switch_to.window(driver.window_handles[1])
                try:
                    driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/a').click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/a'))
                        time.sleep(2)
                        break
                    except Exception as EEe:
                        print("Error: "+str(EEe))
                        clicksubmit(driver)
                        time.sleep(2)
                
            #Closes driver
            try:
                driver.close()
                driver.quit()
            except:
                print("Error closing driver")
            #time.sleep(random.uniform(7.000, 18.000))        
        except Exception as EEE:
            print("Error: "+str(EEE))
            try:
                driver.close()
                driver.quit()
            except:
                print("Error closing driver")
def startthreads(threadnum):
    
    threads = []
    #Optional proxies
    #file = open("proxies.txt","r")
    #proxies = file.readlines()
    #file.close()
    
    #Starts threads
    for i in range(threadnum):
        Thread = threading.Thread(target=go, args=("proxyhere",))    
        threads.append(Thread)
    for thread in threads:
        thread.start()
        time.sleep(random.uniform(5.0, 15.0))
    for thread in threads:
        thread.join()

    
print("""
WELCOME TO TRAFFICBOT V.1
drive bot traffic to any website with high quality proxies
-
""")
urltovisit = str(input("Website: "))
threadstodo = int(input("Threads: "))

startthreads(threadstodo)

print("Beginning organic style traffic flow with high quality scrolling and clicking")
    
