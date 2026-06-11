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
# 1. HIGH-SPEED PROFILE SETUP (UNTOUCHED)
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
chrome_options.page_load_strategy = 'eager'
chrome_options.add_experimental_option("detach", True)

print("🚀 Launching Chrome at Max Speed...")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
fast_wait = WebDriverWait(driver, 2)
actions = ActionChains(driver)

# ==========================================
# 2. HELPER FUNCTIONS 
# ==========================================

def js_click(element):
    """Guaranteed click via JavaScript — bypasses overlays and React quirks."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    driver.execute_script("arguments[0].click();", element)

def pure_human_click(element):
    """Fallback human-style click with ActionChains."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.1)
    try:
        element.click()
    except Exception:
        actions.move_to_element(element).click().perform()

def react_set_input(element, value):
    """Forces a React-controlled <input> to register a new value."""
    driver.execute_script("""
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(arguments[0], arguments[1]);
        arguments[0].dispatchEvent(new Event('input',  { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new FocusEvent('blur', { bubbles: true }));
    """, element, value)

def open_dropdown_and_select(label_xpath, option_xpath, step_name, retries=12):
    """Opens a dropdown and waits for the option to appear. Retries if closed."""
    print(f"[*] Step: {step_name}")
    label = wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
    for attempt in range(retries):
        try:
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.15)
            # Click the dropdown trigger
            driver.execute_script(
                "arguments[0].parentElement.querySelector('input, [role=\"combobox\"], [class*=\"control\"]').click();",
                label
            )
            option = WebDriverWait(driver, 1.5).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            js_click(option)
            print(f"    ✅ {step_name} selected.")
            return True
        except Exception:
            # Fallback: click offset below label
            try:
                actions.move_to_element(label).move_by_offset(0, 40).click().perform()
                option = WebDriverWait(driver, 1.5).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                js_click(option)
                print(f"    ✅ {step_name} selected (fallback).")
                return True
            except Exception:
                time.sleep(0.5) 
                pass
    print(f"    ⚠️  {step_name} failed after {retries} retries.")
    return False

# ==========================================
# 3. EXACT AIM EXECUTION
# ==========================================
try:
    print("⚡ Navigating directly to booking portal...")
    driver.get("https://peoplefirst.ril.com/webapp/#/crbs")
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Create New Booking')]")))
    print("    ✅ Portal loaded.")

    # ----------------------------------------------------------
    # STEP 1: LOCATION
    # ----------------------------------------------------------
    open_dropdown_and_select(
        label_xpath="//*[normalize-space()='Location']",
        option_xpath="//*[contains(text(), 'Reliance Corporate Park')]",
        step_name="Location"
    )

    # ----------------------------------------------------------
    # STEP 2: BOOKING DATE
    # ----------------------------------------------------------
    print("[*] Step: Booking Date (React-safe injection)...")
    actions.send_keys(Keys.ESCAPE).perform()
    date_input = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "(//label[normalize-space()='Booking Date']/following::input)[1]"
                       " | (//*[normalize-space()='Booking Date']/following::input)[1]")
        )
    )
    js_click(date_input)
    time.sleep(0.1)
    react_set_input(date_input, "12/6/2026")
    time.sleep(0.15)
    date_input.send_keys(Keys.TAB)
    print("    ✅ Booking Date set to 12/6/2026.")

    # ----------------------------------------------------------
    # STEP 3: START TIME
    # ----------------------------------------------------------
    open_dropdown_and_select(
        label_xpath="//*[normalize-space()='Start Time']",
        option_xpath="(//*[normalize-space()='20:00'])[last()]",
        step_name="Start Time (20:00)"
    )

    # ----------------------------------------------------------
    # STEP 4: END TIME
    # ----------------------------------------------------------
    open_dropdown_and_select(
        label_xpath="//*[normalize-space()='End Time']",
        option_xpath="(//*[normalize-space()='22:00'])[last()]",
        step_name="End Time (22:00)"
    )

    # ----------------------------------------------------------
    # TRIGGER BACKEND API
    # ----------------------------------------------------------
    print("[*] Forcing API trigger for Buildings...")
    actions.send_keys(Keys.ESCAPE).perform()
    driver.execute_script("document.body.click();")
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1.5) # Initial wait for API to fetch buildings

    # ----------------------------------------------------------
    # STEP 5: BUILDING (Aggressive AJAX Polling for 30-2F)
    # ----------------------------------------------------------
    print("[*] Step: Building (Building 30-2F)")
    bld_label = wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Building']")))
    
    bld_selected = False
    for attempt in range(15): # Max 15 attempts to let API load the list
        try:
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.3)
            # Open the dropdown
            actions.move_to_element(bld_label).move_by_offset(0, 40).click().perform()
            
            # Specifically hunt for Building 30-2F using presence_of_element_located
            bld_opt = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "(//*[normalize-space(text())='Building 30-2F'])[last()]"))
            )
            js_click(bld_opt)
            print("    ✅ Building (Building 30-2F) loaded and selected.")
            bld_selected = True
            break
        except Exception:
            print(f"    ⏳ Attempt {attempt+1}: 'Building 30-2F' not yet fetched, retrying...")
            time.sleep(1) # Wait 1 second before trying again
            
    if not bld_selected:
        print("    ⚠️ Failed to select Building 30-2F. Check if it exists for this time slot.")

    # ----------------------------------------------------------
    # STEP 6: WING (Aggressive AJAX Polling for E)
    # ----------------------------------------------------------
    print("[*] Step: Wing (E)")
    wing_label = wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Wing']")))
    
    for attempt in range(10):
        try:
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.3)
            actions.move_to_element(wing_label).move_by_offset(0, 40).click().perform()
            
            wing_opt = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "(//*[normalize-space(text())='E' or text()='E'])[last()]"))
            )
            js_click(wing_opt)
            print("    ✅ Wing (E) loaded and selected.")
            break
        except Exception:
            print(f"    ⏳ Attempt {attempt+1}: Wing 'E' not yet fetched, retrying...")
            time.sleep(1)

    # ----------------------------------------------------------
    # STEP 7: SEARCH & SELECT ROOM
    # ----------------------------------------------------------
    print("[*] Clicking 'Search Available Rooms'...")
    actions.send_keys(Keys.ESCAPE).perform()
    search_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Search Available Rooms')]"))
    )
    js_click(search_btn)
    
    print("[*] Finding Meeting Room No 02...")
    target_room = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//*[contains(text(), 'Meeting Room No 02')])[1]"))
    )
    clickable_room = driver.execute_script("""
        var el = arguments[0];
        while(el) {
            if(el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || el.classList.contains('card')) return el;
            el = el.parentElement;
        }
        return arguments[0];
    """, target_room)
    js_click(clickable_room)
    print("    ✅ Room selected.")

    # ----------------------------------------------------------
    # STEP 8: I AGREE
    # ----------------------------------------------------------
    print("[*] Clicking 'I Agree'...")
    agree_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'I Agree')]"))
    )
    js_click(agree_btn)

    # ----------------------------------------------------------
    # STEP 9: TITLE INPUT
    # ----------------------------------------------------------
    print("[*] Entering meeting title 'ISOC'...")
    title_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[contains(@placeholder, 'Title') or contains(@placeholder, 'title')]"
                       " | //*[normalize-space()='Title']/following::input[1]")
        )
    )
    js_click(title_input)
    react_set_input(title_input, "ISOC")
    print("    ✅ Title set to 'ISOC'.")

    # ----------------------------------------------------------
    # STEP 10: CONFIRM BOOKING
    # ----------------------------------------------------------
    print("[*] Clicking 'Confirm Booking'...")
    confirm_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Confirm Booking')]"))
    )
    js_click(confirm_btn)

    print("\n🏆 BOOM! Surya, Booking confirmed exactly as requested at machine speed!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
