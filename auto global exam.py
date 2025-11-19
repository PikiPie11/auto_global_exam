#Super parametres

taux_de_reusite = 1
nb_iter = 5






resps = {
    "https://exam.global-exam.com/library/study-sheets/253": [
        "would",
        "eats",
        "will",
        "will",
        "finish",
        "drinks",
        "would",
        "watches",
        "will",
        "sleeps"
    ],
    "https://exam.global-exam.com/library/study-sheets/13": [
        "old",
        "tall",
        "much",
        "long",
        "small",
        "younger",
        "better",
        "more",
        "faster",
        "new"
    ]
    ,"https://exam.global-exam.com/library/study-sheets/260": [
        "always",
        "used to",
        "would",
        "keeps",
        "reads",
        "does",
        "used to",
        "would",
        "visits",
        "enjoy"
    ]
    ,"https://exam.global-exam.com/library/study-sheets/281": [
        "ask",
        "were",
        "concerned",
        "clear",
        "convinced",
        "thought",
        "maintained",
        "firmly",
        "really",
        "pretty"
    ]
    ,"https://exam.global-exam.com/library/study-sheets/283": [
        "shame",
        "poor",
        "nice",
        "wow",
        "see",
        "interesting",
        "me",
        "goodness",
        "dear",
        "seriously"
    ]
}








from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

# Initialisation du WebDriver
driver = webdriver.Chrome()

# Import des identifiants depuis le fichier de configuration
from config import LOGIN_EMAIL, PASSWORD


def random_resp(i, _resps):
    if random.random() >= taux_de_reusite:
        return random.randint(0, len(_resps) - 1)
    return i

def go_to_global_exam():
    driver.get("https://moodle.cesi.fr/course/view.php?id=5157")# a modifier tout les ans
    driver.find_element(By.CLASS_NAME, "btn-ENT").click()

    # Utilisation des identifiants depuis le fichier config
    driver.find_element(By.ID, "login").send_keys(LOGIN_EMAIL)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit"))).click()

    driver.find_element(By.ID, "passwordInput").send_keys(PASSWORD)
    driver.find_element(By.ID, "submitButton").click()

    element = driver.find_element(By.CSS_SELECTOR, ".btn.btn-secondary.btn-block")
    driver.execute_script("arguments[0].click();", element)
    
    element = driver.find_element(By.XPATH, "//a[contains(@onclick, 'window.open')]")
    driver.execute_script("arguments[0].click();", element)

    
    
    
    tabs = driver.window_handles
    driver.switch_to.window(tabs[1])

    driver.get("https://exam.global-exam.com/")

def go_to_activity(link):
    driver.get(link)

    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Je me teste"))
    )
    element.click()
    WebDriverWait(driver, 20).until(EC.url_changes(driver.current_url))

def do_activity(_resps):
    """Remplir automatiquement l'activité avec les réponses"""
    tabs = driver.window_handles
    driver.switch_to.window(tabs[-1])
    
    print(f"URL actuelle : {driver.current_url}")
    
    try:
        # Attendre que la page soit complètement chargée
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
        
        # Trouver tous les champs de texte dans la page
        text_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        print(f"Nombre de champs trouvés : {len(text_inputs)}")
        
        if len(text_inputs) == 0:
            print("Aucun champ de texte trouvé. Recherche alternative...")
            # Essayer de trouver des inputs sans type spécifique
            text_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"Nombre total d'inputs trouvés : {len(text_inputs)}")

        # Remplir chaque champ
        for i in range(min(len(text_inputs), len(_resps))):
            try:
                # S'assurer que l'élément est visible et interactif
                driver.execute_script("arguments[0].scrollIntoView(true);", text_inputs[i])
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(text_inputs[i]))
                
                # Effacer le champ au cas où il contient déjà du texte
                text_inputs[i].clear()
                
                # Saisir la réponse
                response_index = random_resp(i, _resps)
                text_inputs[i].send_keys(_resps[response_index])
                print(f"Champ {i+1} rempli avec : {_resps[response_index]}")
                
            except Exception as e:
                print(f"Erreur lors du remplissage du champ {i+1} : {e}")
                continue

        # Chercher et cliquer sur le bouton de validation
        print("\nRecherche du bouton de validation...")
        
        # Essayer plusieurs sélecteurs pour trouver le bouton
        button_selectors = [
            (By.CLASS_NAME, "min-w-48"),
            (By.XPATH, "//button[contains(text(), 'Valider')]"),
            (By.XPATH, "//button[contains(text(), 'Validate')]"),
            (By.XPATH, "//button[contains(text(), 'Confirm')]"),
            (By.XPATH, "//button[contains(@class, 'validate')]"),
            (By.XPATH, "//button[@type='submit']")
        ]
        
        button_found = False
        for selector_type, selector_value in button_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                button.click()
                print("Bouton de validation cliqué avec succès !")
                button_found = True
                break
            except Exception:
                continue
        
        if not button_found:
            print("Attention : Bouton de validation non trouvé automatiquement")
            print("Vous devrez peut-être valider manuellement")
        
        # Attendre un changement d'URL ou un indicateur de validation
        try:
            WebDriverWait(driver, 20).until(EC.url_changes(driver.current_url))
            print("Activité terminée - URL changée !")
        except Exception:
            print("Activité terminée (pas de changement d'URL détecté)")
            
    except Exception as e:
        print(f"Erreur générale dans do_activity : {e}")



go_to_global_exam()
for i in range(nb_iter):
    index = random.randint(0, len(resps) - 1)
    activity = list(resps.keys())[index]
    go_to_activity(activity)
    do_activity(resps[activity])

driver.quit()