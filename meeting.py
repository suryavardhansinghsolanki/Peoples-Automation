from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

# ==========================================
# 1. HIGH-SPEED PROFILE SETUP
# ==========================================
chrome_options = Options()
profile_path = r"C:\Users\HP\Desktop\MyAutoProfile"
if not os.path.exists(profile_path):
    os.makedirs(profile_path)
    
chrome_options.add_argument(f"user-data-dir={profile_path}") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-allow-origins=*") 
chrome_options.page_load_strategy = 'eager' # Page jaldi load karne ka hack
chrome_options.add_experimental_option("detach", True) 

print("🚀 Launching Chrome at Max Speed...")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10) 
actions = ActionChains(driver)

try:
    # --- ULTRA FAST HUMAN CLICK HELPER ---
    def pure_human_click(element):
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.1) 
        try:
            element.click()
        except:
            actions.move_to_element(element).click().perform()

    # =========================================================
    # INSTANT EXECUTION START (No Timer)
    # =========================================================
    print("⚡ Bypassing menus, jumping direct to booking...")
    driver.get("https://peoplefirst.ril.com/webapp/#/crbs")
    
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Create New Booking')]")))

    # ---------------------------------------------------------
    # STEP 1: LOCATION
    # ---------------------------------------------------------
    actions.send_keys(Keys.ESCAPE).perform() 
    loc_lbl = driver.find_element(By.XPATH, "//*[normalize-space()='Location']")
    actions.move_to_element(loc_lbl).move_by_offset(0, 40).click().perform()
    try:
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search Locations...']")))
        search_box.send_keys("Reliance Corporate Park")
        time.sleep(0.3)
        search_box.send_keys(Keys.ENTER)
    except:
        actions.send_keys("Reliance Corporate Park").pause(0.3).send_keys(Keys.ENTER).perform()

    # ---------------------------------------------------------
    # STEP 2: BOOKING DATE (Direct Injection + React Trigger)
    # ---------------------------------------------------------
    print("[*] Direct Date Injection: 12/6/2026...")
    actions.send_keys(Keys.ESCAPE).perform()
    
    date_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//*[normalize-space()='Booking Date']/following::input)[1]")))
    actions.move_to_element(date_input).click().perform()
    
    date_input.send_keys(Keys.CONTROL + "a")
    date_input.send_keys(Keys.BACKSPACE)
    date_input.send_keys("12/6/2026")
    date_input.send_keys(Keys.TAB)
    
    # HACK: Forcing React to register the date change without clicking calendar
    driver.execute_script("""
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, date_input)
    time.sleep(0.3)

    # ---------------------------------------------------------
    # STEP 3: START TIME
    # ---------------------------------------------------------
    actions.send_keys(Keys.ESCAPE).perform()
    start_lbl = driver.find_element(By.XPATH, "//*[normalize-space()='Start Time']")
    actions.move_to_element(start_lbl).move_by_offset(0, 40).click().perform()
    start_opt = wait.until(EC.element_to_be_clickable((By.XPATH, "(//*[normalize-space()='20:00'])[last()]")))
    pure_human_click(start_opt)

    # ---------------------------------------------------------
    # STEP 4: END TIME 
    # ---------------------------------------------------------
    actions.send_keys(Keys.ESCAPE).perform()
    end_lbl = driver.find_element(By.XPATH, "//*[normalize-space()='End Time']")
    actions.move_to_element(end_lbl).move_by_offset(0, 40).click().perform()
    end_opt = wait.until(EC.element_to_be_clickable((By.XPATH, "(//*[normalize-space()='22:00'])[last()]")))
    pure_human_click(end_opt)
    
    # =========================================================
    # THE MASTER REFRESH HACK (Fake API Trigger)
    # =========================================================
    print("[*] Forcing Backend API to Fetch Buildings...")
    actions.send_keys(Keys.ESCAPE).perform()
    try:
        # Hum bina building bhare ek fake search click mar rahe hain
        dummy_search = driver.find_element(By.XPATH, "//*[contains(text(), 'Search Available Rooms')]")
        pure_human_click(dummy_search)
        time.sleep(1.5) # API ko response dene ka time diya (Ye Page Refresh ka kaam karega)
    except:
        pass

    # ---------------------------------------------------------
    # STEP 5: BUILDING (Machine Speed Polling)
    # ---------------------------------------------------------
    bld_lbl = driver.find_element(By.XPATH, "//*[normalize-space()='Building']")
    
    for attempt in range(10): 
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.2)
        actions.move_to_element(bld_lbl).move_by_offset(0, 40).click().perform()
        try:
            bld_opt = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, "(//*[contains(text(), 'Building 30-2F')])[last()]")))
            pure_human_click(bld_opt)
            break
        except:
            actions.send_keys(Keys.TAB).perform() 

    # ---------------------------------------------------------
    # STEP 6: WING
    # ---------------------------------------------------------
    wing_lbl = driver.find_element(By.XPATH, "//*[normalize-space()='Wing']")
    
    for attempt in range(5):
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.2)
        actions.move_to_element(wing_lbl).move_by_offset(0, 40).click().perform()
        try:
            wing_opt = WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, "(//*[text()='E' or normalize-space()='E'])[last()]")))
            pure_human_click(wing_opt)
            break
        except:
            pass

    # ---------------------------------------------------------
    # FINAL ACTIONS (Machine Speed)
    # ---------------------------------------------------------
    actions.send_keys(Keys.ESCAPE).perform()
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Search Available Rooms')]")))
    pure_human_click(search_btn)
    
    room = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Meeting Room No 02')]")))
    pure_human_click(room)
    
    agree = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'I Agree')]")))
    pure_human_click(agree)
    
    title_el = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Title') or contains(@placeholder, 'title')] | //*[contains(text(), 'Title')]/following::input[1]")))
    title_el.send_keys(Keys.CONTROL + "a")
    title_el.send_keys(Keys.BACKSPACE)
    title_el.send_keys("ISOC")

    confirm = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Confirm Booking')]")))
    pure_human_click(confirm)

    print("\n🏆 BOOM! Surya, Action completed faster than humanly possible!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")